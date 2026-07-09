# GitHub Secrets Setup

These secrets must be added to your GitHub repository for the automation to work.

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

## Required Secrets

### Dropbox (Required)
| Secret Name | Value |
|-------------|-------|
| `DROPBOX_APP_KEY` | `cbhvns42d7eokwc` |
| `DROPBOX_APP_SECRET` | `3jhfft733nq6dch` |
| `DROPBOX_REFRESH_TOKEN` | `Uf0ci92sJVQAAAAAAAAAAXYS6AszCv8NmHNqlIPFwYTBOUcEH7jr9YvGya4JEn1H` |
| `DROPBOX_ACCESS_TOKEN` | (from .env file) |

### Instagram (Required for Instagram upload)
| Secret Name | Value |
|-------------|-------|
| `INSTAGRAM_ACCESS_TOKEN` | (from .env file) |
| `INSTAGRAM_ACCOUNT_ID` | `26555057914080162` |

### Facebook (Required for Facebook upload)
| Secret Name | Value |
|-------------|-------|
| `FACEBOOK_ACCESS_TOKEN` | (from .env file) |
| `FACEBOOK_PAGE_ID` | `1001822213016889` |

### Threads (Required for Threads upload)
| Secret Name | Value |
|-------------|-------|
| `THREADS_ACCESS_TOKEN` | (from .env file) |
| `THREADS_USER_ID` | `26063839556615988` |

### YouTube (Optional - for YouTube Shorts)
| Secret Name | Value |
|-------------|-------|
| `YT_CLIENT_ID` | (from .env file) |
| `YT_CLIENT_SECRET` | (from .env file) |
| `YT_REFRESH_TOKEN` | (from .env file) |

### AI Caption Generation (Required)
| Secret Name | Value |
|-------------|-------|
| `POLLINATIONS_API_KEY` | (from .env file) |

## Schedule

The workflow runs **3 times a day** at:
- 8:00 AM UTC
- 4:00 PM UTC
- 12:00 AM UTC

To change the schedule, edit `.github/workflows/auto_publish.yml`

## Manual Trigger

You can also run the workflow manually:
1. Go to **Actions** tab
2. Select **Auto Publish Videos**
3. Click **Run workflow**
