# Instructions for Running Production Database Migration

## Prerequisites

You need the **production database connection URL** from Vercel. 

### Step 1: Get Database URL from Vercel

1. Go to https://vercel.com/dashboard
2. Select your backend project (Projecte_nJoy)
3. Go to "Settings" → "Environment Variables"
4. Find `DATABASE_URL` or `POSTGRES_URL`
5. Copy the full connection string (it should start with `postgres://` or `postgresql://`)

### Step 2: Create Temporary .env File

Create a file `.env.production` in the `Projecte_nJoy` folder with:

```env
DATABASE_URL=your_production_database_url_here
```

### Step 3: Run Migration

Execute the migration script:

```bash
python run_production_migration.py
```

## What This Migration Does

The migration adds the following columns to your production database:

### TICKET table:
- `scanned_at` (TIMESTAMP, nullable) - Tracks when a ticket was scanned

### USUARIO table:
- `email_verified` (BOOLEAN, default FALSE) - Email verification status
- `verification_token` (VARCHAR(255), nullable) - Token for email verification
- `verification_token_expiry` (TIMESTAMP, nullable) - Token expiration time

## Safety Features

- ✅ Uses `IF NOT EXISTS` checks - safe to run multiple times
- ✅ Non-destructive - only adds columns, doesn't delete data
- ✅ Provides detailed output and verification
- ✅ Shows all columns after migration completes

## Alternative: Manual Execution

If you prefer to run the SQL manually:

1. Connect to your Vercel Postgres database using a SQL client
2. Execute the contents of `migrate_production_db.sql`

## After Migration

Once the migration completes successfully:
1. Your production API should work without the `scanned_at` error
2. Email verification functionality will be available
3. No data will be lost from existing tables
