import cesium from 'vite-plugin-cesium';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({ 
    define: {
      "process.env": {
        NODE_DEBUG: false,
      },
      global: "globalThis",
    },
    plugins: [sveltekit()] 
});
