import { defineConfig } from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';
import ffmpeg from '@motion-canvas/ffmpeg';

export default defineConfig({
  plugins: [motionCanvas(), ffmpeg()],
  server: {
    watch: {
      ignored: ['**/venv/**', '**/scripts/**', '**/my-animation/reports/**', '**/output/**', '**/files/**', '**/__pycache__/**', '**/*.pyc', '**/*.pyo', '**/node_modules/**']
    },
    // Windows-specific optimizations
    fs: {
      strict: false
    }
  },
});
