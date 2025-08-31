#!/usr/bin/env node
/**
 * Script pour diagnostiquer et corriger l'erreur ChunkLoadError
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Diagnostic de l\'erreur ChunkLoadError');
console.log('=' .repeat(60));

// 1. Vérifier la structure des dossiers
console.log('\n📁 Vérification de la structure des dossiers...');
const requiredDirs = ['.next', 'node_modules', 'app'];
const missingDirs = [];

requiredDirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    missingDirs.push(dir);
    console.log(`❌ Dossier manquant: ${dir}`);
  } else {
    console.log(`✅ Dossier présent: ${dir}`);
  }
});

if (missingDirs.length > 0) {
  console.log(`\n⚠️  Dossiers manquants: ${missingDirs.join(', ')}`);
}

// 2. Vérifier les fichiers de configuration
console.log('\n📄 Vérification des fichiers de configuration...');
const configFiles = [
  'package.json',
  'next.config.ts',
  'tsconfig.json',
  'tailwind.config.js'
];

configFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}: Présent`);
  } else {
    console.log(`❌ ${file}: Manquant`);
  }
});

// 3. Vérifier les dépendances
console.log('\n📦 Vérification des dépendances...');
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const requiredDeps = ['next', 'react', 'react-dom'];
  
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`✅ ${dep}: ${packageJson.dependencies[dep]}`);
    } else if (packageJson.devDependencies && packageJson.devDependencies[dep]) {
      console.log(`✅ ${dep}: ${packageJson.devDependencies[dep]} (dev)`);
    } else {
      console.log(`❌ ${dep}: Manquant`);
    }
  });
} catch (error) {
  console.log(`❌ Erreur lors de la lecture de package.json: ${error.message}`);
}

// 4. Nettoyer le cache
console.log('\n🧹 Nettoyage du cache...');
try {
  if (fs.existsSync('.next')) {
    fs.rmSync('.next', { recursive: true, force: true });
    console.log('✅ Cache .next supprimé');
  }
  
  if (fs.existsSync('node_modules/.cache')) {
    fs.rmSync('node_modules/.cache', { recursive: true, force: true });
    console.log('✅ Cache node_modules supprimé');
  }
} catch (error) {
  console.log(`⚠️  Erreur lors du nettoyage: ${error.message}`);
}

// 5. Recommandations
console.log('\n💡 Recommandations pour corriger l\'erreur ChunkLoadError:');
console.log('1. Arrêtez le serveur de développement (Ctrl+C)');
console.log('2. Exécutez: npm run build');
console.log('3. Puis: npm run dev');
console.log('4. Si le problème persiste, essayez: npm run dev -- --turbo');
console.log('5. Ou désactivez temporairement le cache: npm run dev -- --no-cache');

console.log('\n' + '=' .repeat(60));
