-- Script pour corriger les politiques Supabase
-- Exécutez ce script dans l'éditeur SQL de Supabase

-- 1. Désactiver RLS temporairement sur la table users
ALTER TABLE auth.users DISABLE ROW LEVEL SECURITY;

-- 2. Supprimer les politiques problématiques
DROP POLICY IF EXISTS "Users can view own profile" ON auth.users;
DROP POLICY IF EXISTS "Users can update own profile" ON auth.users;
DROP POLICY IF EXISTS "Users can insert own profile" ON auth.users;

-- 3. Créer des politiques simples et sécurisées
CREATE POLICY "Users can view own profile" ON auth.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON auth.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON auth.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 4. Réactiver RLS
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- 5. Vérifier les politiques existantes
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'users';
