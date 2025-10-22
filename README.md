# one-time fresh start (drops volume, recreates, migrates, seeds, runs api)
.\scripts\setup\db.ps1 -Init
.\scripts\setup\run.ps1 -Seed

# normal day-to-day (start everything, migrate, run api; no seeding)
.\scripts\setup\run.ps1

# only reseed (when API already running)
.\scripts\db\seed-database.ps1
