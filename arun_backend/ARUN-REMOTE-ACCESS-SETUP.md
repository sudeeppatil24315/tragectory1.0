# PostgreSQL Remote Access Setup for Arun

**Purpose:** Allow remote connection from another PC to your PostgreSQL database  
**Time:** 5-10 minutes  
**Risk:** Low (we'll use password authentication)

---

## Step 1: Find Your IP Address

Open Command Prompt and run:
```bash
ipconfig
```

Look for **IPv4 Address** under your active network adapter (WiFi or Ethernet).

**Example:**
```
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

**Write down this IP address:** `_________________`

Share this IP with the person who will connect remotely.

---

## Step 2: Configure PostgreSQL to Accept Remote Connections

### 2.1 Find PostgreSQL Data Directory

Your PostgreSQL is likely installed in:
```
C:\Program Files\PostgreSQL\14\data\
```

Or check in pgAdmin:
- Right-click on your server
- Properties → General → Data directory

### 2.2 Edit postgresql.conf

**Location:** `C:\Program Files\PostgreSQL\14\data\postgresql.conf`

1. Open the file with **Notepad as Administrator**
2. Find this line (around line 59):
```conf
#listen_addresses = 'localhost'
```

3. Change it to:
```conf
listen_addresses = '*'
```

4. Save the file

**What this does:** Allows PostgreSQL to accept connections from any IP address.

### 2.3 Edit pg_hba.conf

**Location:** `C:\Program Files\PostgreSQL\14\data\pg_hba.conf`

1. Open the file with **Notepad as Administrator**
2. Scroll to the bottom
3. Add this line (replace `REMOTE_PC_IP` with the IP of the PC that will connect):

```conf
# Allow remote connection from specific IP
host    trajectory    postgres    REMOTE_PC_IP/32    md5
```

**Example:** If the remote PC's IP is `192.168.1.50`:
```conf
host    trajectory    postgres    192.168.1.50/32    md5
```

**Or allow any IP on your local network (less secure but easier):**
```conf
host    trajectory    postgres    192.168.1.0/24    md5
```

4. Save the file

**What this does:** Allows the specific IP (or IP range) to connect to the `trajectory` database using password authentication.

---

## Step 3: Configure Windows Firewall

### Option A: Allow PostgreSQL Through Firewall (Recommended)

1. Open **Windows Defender Firewall with Advanced Security**
   - Press `Win + R`
   - Type: `wf.msc`
   - Press Enter

2. Click **Inbound Rules** → **New Rule**

3. Select **Port** → Next

4. Select **TCP** and enter port: `5432` → Next

5. Select **Allow the connection** → Next

6. Check all profiles (Domain, Private, Public) → Next

7. Name: `PostgreSQL Remote Access` → Finish

### Option B: Temporarily Disable Firewall (For Testing Only)

**⚠️ Warning:** Only do this for testing, then re-enable it!

1. Open **Windows Security**
2. Go to **Firewall & network protection**
3. Click your active network (Private/Public)
4. Turn off **Windows Defender Firewall**

**Remember to turn it back on after testing!**

---

## Step 4: Restart PostgreSQL Service

1. Press `Win + R`
2. Type: `services.msc`
3. Press Enter
4. Find **postgresql-x64-14** (or your version)
5. Right-click → **Restart**

**Or use Command Prompt as Administrator:**
```bash
net stop postgresql-x64-14
net start postgresql-x64-14
```

---

## Step 5: Test Local Connection (Verify It Still Works)

```bash
psql -U postgres -d trajectory
```

Enter password: `8088`

If you can connect, PostgreSQL is running correctly!

Type `\q` to exit.

---

## Step 6: Share Connection Details

Send these details to the person who will connect remotely:

```
PostgreSQL Connection Details:
- Host: YOUR_IP_ADDRESS (e.g., 192.168.1.100)
- Port: 5432
- Database: trajectory
- Username: postgres
- Password: 8088
```

---

## Step 7: Test Remote Connection

The remote PC should test the connection:

```bash
psql -h YOUR_IP -U postgres -d trajectory
```

**Example:**
```bash
psql -h 192.168.1.100 -U postgres -d trajectory
```

If it works, you'll see:
```
Password for user postgres:
trajectory=#
```

---

## Troubleshooting

### Issue 1: "Connection refused"

**Possible causes:**
- PostgreSQL service not running
- Firewall blocking port 5432
- Wrong IP address

**Solutions:**
1. Check PostgreSQL service is running
2. Check firewall rule is created
3. Verify IP address with `ipconfig`

### Issue 2: "Connection timed out"

**Possible causes:**
- Firewall blocking connection
- Not on same network
- Router blocking traffic

**Solutions:**
1. Temporarily disable firewall to test
2. Make sure both PCs are on same WiFi/network
3. Check router settings

### Issue 3: "Authentication failed"

**Possible causes:**
- Wrong password
- pg_hba.conf not configured correctly

**Solutions:**
1. Verify password is `8088`
2. Check pg_hba.conf has the correct IP
3. Restart PostgreSQL after changes

### Issue 4: "Database does not exist"

**Solution:**
```sql
-- Connect as postgres
psql -U postgres

-- Create database
CREATE DATABASE trajectory;

-- Exit
\q
```

---

## Security Notes

### For Development (Current Setup):
✅ Password authentication (md5)  
✅ Specific IP or local network only  
✅ Firewall rule for port 5432  

### For Production (Future):
- Use SSL/TLS encryption
- Use stronger passwords
- Limit to specific IPs only
- Use VPN for remote access
- Regular security audits

---

## Reverting Changes (If Needed)

If you want to disable remote access later:

### 1. Edit postgresql.conf
Change back to:
```conf
listen_addresses = 'localhost'
```

### 2. Edit pg_hba.conf
Remove or comment out the remote access line:
```conf
# host    trajectory    postgres    192.168.1.50/32    md5
```

### 3. Restart PostgreSQL
```bash
net stop postgresql-x64-14
net start postgresql-x64-14
```

---

## Summary Checklist

- [ ] Found my IP address: `_________________`
- [ ] Edited postgresql.conf (listen_addresses = '*')
- [ ] Edited pg_hba.conf (added remote IP)
- [ ] Configured Windows Firewall (port 5432)
- [ ] Restarted PostgreSQL service
- [ ] Tested local connection (still works)
- [ ] Shared connection details with remote PC
- [ ] Remote PC tested connection (successful)

---

## Questions?

- **Is this safe?** Yes, for local network development. We're using password authentication and can limit to specific IPs.
- **Will this slow down my PC?** No, minimal impact.
- **Can I undo this?** Yes, follow the "Reverting Changes" section.
- **Do I need to do this every time?** No, only once. The settings persist.

---

**Status:** Ready for remote access setup  
**Next:** Remote PC can run Alembic migrations
