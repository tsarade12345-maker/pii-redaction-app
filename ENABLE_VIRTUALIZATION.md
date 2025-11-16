# How to Enable Virtualization for Docker Desktop

If you want to use Docker Desktop later, you need to enable virtualization in your BIOS/UEFI settings.

## Step 1: Check if Virtualization is Enabled

Open PowerShell as Administrator and run:

```powershell
Get-ComputerInfo -Property "HyperV*"
```

Or check in Task Manager:
1. Press `Ctrl + Shift + Esc` to open Task Manager
2. Go to "Performance" tab
3. Click "CPU"
4. Look for "Virtualization" - it should say "Enabled"

## Step 2: Enable Virtualization in BIOS/UEFI

### For Most Computers:

1. **Restart your computer**
2. **Enter BIOS/UEFI Setup:**
   - **Dell/HP/Lenovo:** Press `F2` or `F12` during startup
   - **ASUS:** Press `F2` or `Delete`
   - **Acer:** Press `F2` or `Delete`
   - **MSI:** Press `Delete`
   - Look for message like "Press [KEY] to enter Setup"

3. **Find Virtualization Settings:**
   - Look for "Virtualization Technology" or "VT-x" (Intel) or "AMD-V" (AMD)
   - May be under:
     - "Advanced" → "CPU Configuration"
     - "Advanced" → "Processor Configuration"
     - "Security" → "Virtualization"
     - "System Configuration" → "Virtualization Technology"

4. **Enable Virtualization:**
   - Set to "Enabled"
   - Save and Exit (usually `F10`)

5. **Restart your computer**

## Step 3: Enable Windows Features

After enabling in BIOS, enable Windows features:

1. **Open PowerShell as Administrator:**
   - Right-click Start button
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Enable required features:**
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
   Enable-WindowsOptionalFeature -Online -FeatureName Containers
   ```

3. **Restart your computer**

## Step 4: Verify Virtualization

After restart, check again:

```powershell
Get-ComputerInfo -Property "HyperV*"
```

Or in Task Manager → Performance → CPU, check "Virtualization" status.

## Step 5: Restart Docker Desktop

1. Open Docker Desktop
2. Click "Restart" if prompted
3. Wait for Docker to fully start

## Alternative: Use WSL 2 Backend

If you have Windows 10/11 Pro, you can also use WSL 2:

1. Install WSL 2:
   ```powershell
   wsl --install
   ```

2. Restart computer

3. Configure Docker Desktop to use WSL 2 backend:
   - Docker Desktop → Settings → General
   - Check "Use the WSL 2 based engine"

## Still Having Issues?

### Check System Requirements:
- 64-bit processor with Second Level Address Translation (SLAT)
- 4GB system RAM minimum
- BIOS-level hardware virtualization support

### Contact IT Admin:
If this is a work computer, virtualization may be disabled by IT policy. Contact your IT administrator to enable it.

### Use Local Development Instead:
You can run the application locally without Docker (see `RUN_LOCALLY.md`)

