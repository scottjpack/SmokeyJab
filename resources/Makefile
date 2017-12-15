rat: rat.c
	gcc -Os -s -o $@ $^
	@strip -s $@
	@echo -e '\n\n Finished building, press [ENTER] to get base64-encoded ELF for the script.\n'
	@/bin/bash -c "read"
	@base64 -w0 $@
