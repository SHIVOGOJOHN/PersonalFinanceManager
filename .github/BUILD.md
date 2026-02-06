# GitHub Actions Build

## Automated APK Building

This project uses GitHub Actions to automatically build Android APK files.

### How It Works

1. **Automatic Builds**: Every push to `main` branch triggers a build
2. **Manual Builds**: You can trigger builds manually from GitHub Actions tab
3. **Download APK**: After build completes, download from Actions artifacts

### Downloading Your APK

1. Go to your GitHub repository
2. Click on **Actions** tab
3. Click on the latest workflow run
4. Scroll down to **Artifacts** section
5. Download `finance-manager-apk.zip`
6. Extract the APK file

### Build Time

- **First build**: ~15-20 minutes (downloads Android SDK/NDK)
- **Subsequent builds**: ~10-15 minutes (cached dependencies)

### Manual Trigger

To manually trigger a build:

1. Go to **Actions** tab
2. Click **Build Android APK** workflow
3. Click **Run workflow** button
4. Select branch and click **Run workflow**

### Build Status

Check build status with the badge:

```markdown
![Build Status](https://github.com/YOURUSERNAME/YOURREPO/workflows/Build%20Android%20APK/badge.svg)
```

### Troubleshooting

**Build Failed?**
- Check the workflow logs in Actions tab
- Common issues: buildozer.spec configuration, missing dependencies
- Re-run the workflow if it was a temporary issue

**APK Not Generated?**
- Ensure buildozer.spec is properly configured
- Check that all required files are committed
- Verify Python version compatibility

### Creating Releases

To create a release with APK:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The APK will be automatically attached to the GitHub release.
