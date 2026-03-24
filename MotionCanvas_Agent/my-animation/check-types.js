#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

// Get the file to check from command line arguments
const fileToCheck = process.argv[2];

if (!fileToCheck) {
  console.error('Usage: node check-types.js <file-path>');
  process.exit(1);
}

// Create a temporary tsconfig that includes only the specific file
const tempTsConfig = {
  extends: '@motion-canvas/2d/tsconfig.project.json',
  include: [fileToCheck],
  compilerOptions: {
    target: 'es2020',
    module: 'esnext',
    lib: ['dom', 'esnext'],
    jsx: 'react-jsx',
    jsxImportSource: '@motion-canvas/2d/lib',
    strict: true,
    esModuleInterop: true,
    skipLibCheck: true,
    forceConsistentCasingInFileNames: true,
    moduleResolution: 'node',
    allowSyntheticDefaultImports: true,
    isolatedModules: true,
    downlevelIteration: true,
    experimentalDecorators: true,
    noImplicitAny: false,
    strictNullChecks: false,
    types: ['vite/client'],
    noEmit: true
  }
};

const fs = require('fs');
const tempConfigPath = 'tsconfig.temp.json';

try {
  // Write temporary config
  fs.writeFileSync(tempConfigPath, JSON.stringify(tempTsConfig, null, 2));
  
  // Run TypeScript with the temporary config
  execSync(`npx tsc --project ${tempConfigPath}`, { 
    stdio: 'inherit',
    cwd: process.cwd()
  });
  
  console.log(`✅ No type errors found in ${fileToCheck}`);
} catch (error) {
  console.log(`❌ Type errors found in ${fileToCheck}`);
  process.exit(1);
} finally {
  // Clean up temporary config
  if (fs.existsSync(tempConfigPath)) {
    fs.unlinkSync(tempConfigPath);
  }
}
