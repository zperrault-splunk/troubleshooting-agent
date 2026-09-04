---
title: "Connect to EC2 Instance"
description: "Connect to your workshop EC2 instance, retrieve your instance name, and optionally set up VS Code remote editing."
weight: 3
navTitle: "Connect to EC2 Instance"
duration: "5 minutes"
---

An Ubuntu Linux EC2 instance is ready for you. To find its connection details:

- Open the **Splunk Show** event for your region.
- Click **Enroll** in the upper-right corner.
- Scroll toward the bottom of the page to your EC2 instance details.

You should see connection information such as the following:

{{< diagram src="images/ConnectionInformation.png" alt="Splunk Show EC2 connection information with SSH command and password" >}}

Use the IP address in **SSH Command** and the **SSH Password** from **Connection Information** to connect:

- **macOS or Linux:** `ssh splunk@IP address`
- **Windows 10 or later:** Use the OpenSSH client.
- **Earlier Windows versions:** Use PuTTY.

{{< notice title="Note" style="primary" >}}
Answer **yes** when asked if you want to continue connecting.
{{< /notice >}}

{{< diagram src="images/signInEC2.png" alt="Terminal prompt asking to confirm SSH connection fingerprint" >}}

{{< notice title="VPN Connection" style="green" >}}

If you are in an office and the SSH connection fails, connect to your corporate VPN and try again.

{{< /notice >}}

## Retrieve your instance name

After you connect over SSH, retrieve your instance name:

```bash
echo $INSTANCE
```

Save the printed value. It uniquely identifies your instance and later helps you find your data in Splunk Observability Cloud.

## Connect Visual Studio Code (optional)

{{< notice title="Tip" style="tip" >}}
You will edit several files during the workshop. The instructions use `vi`, but you can use VS Code instead.
{{< /notice >}}

To use a full IDE, connect VS Code on your laptop to the EC2 instance and edit the remote files directly.

1. [Download and install VS Code](https://code.visualstudio.com/download).
2. In VS Code, open **Settings**, then **Extensions**.
3. Search for the **Remote – SSH extension** (by Microsoft) and install it.

{{< diagram src="images/InstallRemoteSSH.png" alt="VS Code Extensions view showing Remote SSH extension" >}}

1. Press **F1** (or Ctrl+Shift+P on Windows / Cmd+Shift+P on macOS).
2. Run **Remote-SSH: Connect to Host**.
3. Copy your SSH command from Splunk Show: `ssh -p 2222 splunk@EC2_PUBLIC_IP`.
4. Choose the default SSH config file when prompted.
5. Press **F1** (or Ctrl+Shift+P on Windows / Cmd+Shift+P on macOS) again.
6. Run **Remote-SSH: Connect to Host**.
7. Select the host you just added. VS Code will open a new window and start the connection.
8. When VS Code prompts for the **SSH password**, enter the password from Splunk Show.
9. Click **Open Folder**, then enter `/home/splunk`:

{{< diagram src="images/OpenRemoteFolder.png" alt="VS Code Open Folder dialog with /home/splunk path" >}}

VS Code is now editing files on the EC2 instance.