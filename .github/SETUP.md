# GitHub Actions Setup

## Required Secrets

To enable the automated release workflow, you need to create a Personal Access Token (PAT) and add it as a repository secret.

### Creating a Personal Access Token (PAT)

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
   - Direct link: https://github.com/settings/tokens/new

2. Click **Generate new token** → **Generate new token (classic)**

3. Configure the token:
   - **Note**: `StravaFetcher Release Automation`
   - **Expiration**: Choose your preferred expiration (recommend 90 days or 1 year)
   - **Scopes**: Select the following:
     - ✅ `repo` (Full control of private repositories)
       - This includes `repo:status`, `repo_deployment`, `public_repo`, etc.
     - ✅ `workflow` (Update GitHub Action workflows)

4. Click **Generate token** at the bottom

5. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

### Adding the Secret to Your Repository

1. Go to your repository: https://github.com/hope0hermes/StravaFetcher

2. Navigate to **Settings** → **Secrets and variables** → **Actions**
   - Direct link: https://github.com/hope0hermes/StravaFetcher/settings/secrets/actions

3. Click **New repository secret**

4. Configure the secret:
   - **Name**: `PAT_TOKEN`
   - **Value**: Paste the Personal Access Token you created
   - Click **Add secret**

### Verification

After adding the secret:
1. The release workflow will be able to create PRs automatically
2. Merge any PR with `feat!:`, `feat:`, or `fix:` commits to test the automation
3. The workflow should create a version bump PR
4. After merging the version bump PR, a GitHub Release will be created automatically

### Security Notes

- The PAT has access to all your repositories, so keep it secure
- Consider creating a dedicated GitHub account (bot account) for automation if working in a team
- Set an expiration date and create a calendar reminder to renew it
- Never commit the token to the repository
- You can revoke the token at any time from https://github.com/settings/tokens

### Troubleshooting

If the workflow fails with "GitHub Actions is not permitted to create or approve pull requests":
- Verify the `PAT_TOKEN` secret exists and is correctly named
- Verify the PAT has the `repo` and `workflow` scopes
- Check if the PAT has expired
- Ensure you're using a classic PAT, not a fine-grained token (fine-grained tokens may have issues with some operations)
