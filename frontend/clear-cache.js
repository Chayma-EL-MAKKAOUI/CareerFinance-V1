#!/usr/bin/env node
/**
 * Script pour nettoyer le cache Next.js et corriger l'erreur ChunkLoadError
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🧹 Nettoyage du cache Next.js...');
console.log('=' .repeat(50));

// 1. Supprimer le dossier .next
const nextDir = path.join(__dirname, '.next');
if (fs.existsSync(nextDir)) {
  console.log('🗑️  Suppression du dossier .next...');
  fs.rmSync(nextDir, { recursive: true, force: true });
  console.log('✅ Dossier .next supprimé');
} else {
  console.log('ℹ️  Dossier .next non trouvé');
}

// 2. Supprimer le cache node_modules
const cacheDir = path.join(__dirname, 'node_modules', '.cache');
if (fs.existsSync(cacheDir)) {
  console.log('🗑️  Suppression du cache node_modules...');
  fs.rmSync(cacheDir, { recursive: true, force: true });
  console.log('✅ Cache node_modules supprimé');
} else {
  console.log('ℹ️  Cache node_modules non trouvé');
}

// 3. Nettoyer le cache npm
console.log('🧹 Nettoyage du cache npm...');
try {
  execSync('npm cache clean --force', { stdio: 'inherit' });
  console.log('✅ Cache npm nettoyé');
} catch (error) {
  console.log('⚠️  Erreur lors du nettoyage du cache npm');
}

console.log('\n🎉 Nettoyage terminé !');
console.log('\n📝 Prochaines étapes:');
console.log('1. Redémarrez le serveur de développement: npm run dev');
console.log('2. Si le problème persiste, essayez: npm run dev -- --turbo');
console.log('3. Ou désactivez le cache: npm run dev -- --no-cache');

console.log('\n' + '=' .repeat(50));
