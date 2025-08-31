-- Configuration Supabase pour l'authentification et RLS
-- À exécuter dans l'éditeur SQL de Supabase

-- 1. Activer l'extension pgcrypto pour le hachage bcrypt
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Créer la table users si elle n'existe pas
CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    document_analyses_count INTEGER DEFAULT 0,
    salary_analyses_count INTEGER DEFAULT 0,
    coaching_sessions_count INTEGER DEFAULT 0,
    last_login TIMESTAMPTZ,
    auth_id UUID -- Pour lier avec Supabase Auth
);

-- 3. Créer les fonctions d'authentification

-- Fonction d'inscription
CREATE OR REPLACE FUNCTION register_user(
    p_email VARCHAR(255),
    p_username VARCHAR(50),
    p_password VARCHAR(255),
    p_first_name VARCHAR(100),
    p_last_name VARCHAR(100),
    p_role VARCHAR(20) DEFAULT 'user'
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id BIGINT;
    v_result JSON;
BEGIN
    -- Vérifier si l'email ou username existe déjà
    IF EXISTS (SELECT 1 FROM public.users WHERE email = p_email OR username = p_username) THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Email ou username déjà utilisé'
        );
    END IF;
    
    -- Insérer le nouvel utilisateur
    INSERT INTO public.users (
        email, username, password, first_name, last_name, role
    ) VALUES (
        p_email, p_username, crypt(p_password, gen_salt('bf')), 
        p_first_name, p_last_name, p_role
    ) RETURNING id INTO v_user_id;
    
    -- Retourner le succès
    RETURN json_build_object(
        'success', true,
        'user_id', v_user_id,
        'message', 'Utilisateur créé avec succès'
    );
    
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'error', SQLERRM
    );
END;
$$;

-- Fonction de connexion
CREATE OR REPLACE FUNCTION login_user(
    p_email VARCHAR(255),
    p_password VARCHAR(255)
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user RECORD;
    v_result JSON;
BEGIN
    -- Vérifier les credentials
    SELECT id, username, email, first_name, last_name, role, is_active, password
    INTO v_user
    FROM public.users 
    WHERE email = p_email AND is_active = true;
    
    -- Vérifier si l'utilisateur existe et le mot de passe est correct
    IF v_user.id IS NULL OR NOT (crypt(p_password, v_user.password) = v_user.password) THEN
        RETURN json_build_object(
            'success', false,
            'error', 'Email ou mot de passe incorrect'
        );
    END IF;
    
    -- Mettre à jour last_login
    UPDATE public.users 
    SET last_login = NOW() 
    WHERE id = v_user.id;
    
    -- Retourner les informations utilisateur (sans le mot de passe)
    RETURN json_build_object(
        'success', true,
        'user', json_build_object(
            'id', v_user.id,
            'username', v_user.username,
            'email', v_user.email,
            'first_name', v_user.first_name,
            'last_name', v_user.last_name,
            'role', v_user.role,
            'is_active', v_user.is_active,
            'last_login', NOW()
        )
    );
    
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'error', SQLERRM
    );
END;
$$;

-- 4. Activer RLS sur toutes les tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coaching_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rag_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyse_doc_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doc_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.negociations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.formation ENABLE ROW LEVEL SECURITY;

-- 5. Créer les politiques RLS

-- Politique pour users (chaque utilisateur ne voit que ses propres données)
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid()::text = auth_id::text OR id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid()::text = auth_id::text OR id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Politique pour chat_sessions
CREATE POLICY "Users can manage own chat sessions" ON public.chat_sessions
    FOR ALL USING (user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Politique pour documents
CREATE POLICY "Users can manage own documents" ON public.documents
    FOR ALL USING (user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Politique pour coaching_sessions
CREATE POLICY "Users can manage own coaching sessions" ON public.coaching_sessions
    FOR ALL USING (user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Politique pour rag_queries
CREATE POLICY "Users can manage own rag queries" ON public.rag_queries
    FOR ALL USING (user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid()));

-- Politique pour analyse_doc_results (via documents)
CREATE POLICY "Users can manage own doc analysis results" ON public.analyse_doc_results
    FOR ALL USING (
        document_id IN (
            SELECT id FROM public.documents 
            WHERE user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        )
    );

-- Politique pour doc_chunks (via documents)
CREATE POLICY "Users can manage own doc chunks" ON public.doc_chunks
    FOR ALL USING (
        doc_id IN (
            SELECT id FROM public.documents 
            WHERE user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        )
    );

-- Politique pour negociations (via coaching_sessions)
CREATE POLICY "Users can manage own negotiations" ON public.negociations
    FOR ALL USING (
        coaching_session_id IN (
            SELECT id FROM public.coaching_sessions 
            WHERE user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        )
    );

-- Politique pour formation (via coaching_sessions)
CREATE POLICY "Users can manage own formations" ON public.formation
    FOR ALL USING (
        coaching_session_id IN (
            SELECT id FROM public.coaching_sessions 
            WHERE user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        )
    );

-- 6. Créer un trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7. Créer un index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON public.users(auth_id);
