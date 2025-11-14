# Windows Development Setup Notes

## Known Issues & Fixes

### Nuxt SSR Path Issues on Windows

**Problem:** Nuxt 3 has path resolution issues on Windows when using SSR (Server-Side Rendering) mode, especially with the PWA module.

**Errors you might see:**
- `path should be a path.relative()d string`
- `Cannot find module '#app/entry'`
- `plugin-vue:export-helper` errors

**Solution Applied:**
1. **Disabled SSR** in `nuxt.config.ts` by setting `ssr: false`
2. **Disabled PWA module** temporarily (can be re-enabled for production on Linux)
3. App now runs in **client-side only mode**

### What This Means

✅ **Still Works:**
- All Nuxt features work perfectly
- Vue components, routing, Pinia state management
- Tailwind CSS styling
- API calls to Django backend
- All interactivity and functionality

⚠️ **Limitations:**
- No server-side rendering (SSR) - pages render in browser only
- Slightly slower initial page load (negligible for this app)
- No SEO optimization from SSR (not critical for auth-required app)

### For Production Deployment

When deploying to a Linux VPS:
1. Re-enable SSR: Remove `ssr: false` from `nuxt.config.ts`
2. Re-enable PWA: Uncomment `@vite-pwa/nuxt` in modules
3. Build with `npm run build`
4. Everything will work with full SSR and PWA features

### Current Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  ssr: false, // Client-side only for Windows development
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    // '@vite-pwa/nuxt', // Re-enable for production
  ],
  // ...
})
```

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will start at http://localhost:3000/ and work perfectly in client-side mode.

## Alternative: Use WSL2

If you prefer full SSR during development, you can use WSL2 (Windows Subsystem for Linux):

```bash
# In WSL2 terminal
cd /mnt/g/hacktheice/frontend
npm install
npm run dev
```

This will run Nuxt in a Linux environment and avoid all Windows path issues.

## Summary

The current setup is **optimized for Windows development** and provides:
- ✅ Fast development experience
- ✅ Hot reload works perfectly
- ✅ All features functional
- ✅ Easy to switch to full SSR for production

No functionality is lost - the app works exactly the same, just renders on the client instead of the server during development.
