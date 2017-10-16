# SmokeyJab
SmokeyJab is a framework that tests your security ecosystem from endpoint to analyst, like a modular EICAR test for the enterprise.

### Requirements
#### Endpoint
- Python 2.6 or 2.7
- Root privileges, for some of the modules
#### Monitoring
- Splunk HEC (timestamps/artifacts are logged to Splunk)

### Provisioning
```
usage: provision.py [-h] [-v] [-d] [-b BANNER] [-n SCRIPT_NAME] -u SPLUNK_HOST
                    -t SPLUNK_TOKEN
                    project

positional arguments:
  project               The name of the project this is running under

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose logging
  -d, --debug           Enable debug logging
  -b BANNER, --banner BANNER
                        Tag to insert into artifacts for identification
                        purposes
  -n SCRIPT_NAME, --script-name SCRIPT_NAME
                        New name for the script in the process list
  -u SPLUNK_HOST, --splunk-host SPLUNK_HOST
                        The host (server[:port]) of the splunk HEC
  -t SPLUNK_TOKEN, --splunk-token SPLUNK_TOKEN
                        Splunk HEC token
```
- -v/-d: Enable verbose/debug output during provisioning
- -b: A text string to include in endpoint artifacts where possible
- -n: How you want SmokeyJab to appear in the process list
- -u: The hostname/IP of your Splunk HEC server
- -t: A HEC token to be used for SmokeyJab events (should be assigned a default index)

### Copying to/executing on target
The name generated for your script by the provisioning process is important; whatever the
script name is on target, should be at least as long as the auto-generated name to ensure
the process-list dorking functionality works.

Simply execute your script by invoking Python normally, and backgrounding the process:
```bash
# python extreme_nubby_hubbub.py &
[1] 321987
# disown %1
```

You should see events start to flow into your Splunk instance immediately