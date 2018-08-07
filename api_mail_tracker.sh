#!/bin/bash

PGSQLNONCE=`grep 'pgsql_nonce' /data1/message_studio/conf/msgstudio.conf |cut -d= -f2`
PGSQLPASS=`grep 'pgsql_password' /data1/message_studio/conf/msgstudio.conf |cut -d= -f2`
PGPASSWORD=`JAVA_HOME="/data1/message_studio/thirdparty/java64/jre1.7.0"; JAVA_CLASSPATH='/data1/message_studio/lib/sm/WEB-INF:/data1/message_studio/lib/sm/WEB-INF/lib/*:/data1/message_studio/lib/sm/WEB-INF/classes:/data1/message_studio/lib/bfj220.jar:/data1/message_studio/lib/sm/WEB-INF/lib/sm_common_business.jar:/data1/message_studio/lib/sm/WEB-INF/lib/commons-lang-2.1.jar:/data1/message_studio/lib/sm/WEB-INF/lib/commons-logging-1.0.4.jar:/data1/message_studio/lib/sm/WEB-INF/lib/spring.jar:/data1/message_studio/lib/sm/WEB-INF/lib/postgresql-8.0-310.jdbc3.jar:/data1/message_studio/lib/sm/WEB-INF/lib/mysql-connector-java-5.1.16-bin.jar:/data1/message_studio/lib/sm/WEB-INF/lib/log4j-1.2.14.jar:/data1/message_studio/lib/sm/WEB-INF/lib/commons-io-2.0.1.jar'; ${JAVA_HOME}/bin/java -cp ${JAVA_CLASSPATH} com.sm.common.business.security.StrongMailSymmetricEncryptionUtility D $PGSQLPASS $PGSQLNONCE`

Today=`date +"%Y-%m-%d"`
AppServerLog=/data1/message_studio/log/system/appserver.log
DBFile=`find /data1/strongmail/data/databases/ -name 1*.db -mtime -1`
RetryLOG=/data1/strongmail/log/strongmail-retryfailed.log
SuccessLOG=/data1/strongmail/log/strongmail-success.log
BCCSuccessLOG=/data1/strongmail/log/strongmail-success-bcc-cc.log
BCCRetryLOG=/data1/strongmail/log/strongmail-retryfailed-bcc-cc.log
MTASERVERS=`grep HostName /data1/strongmail/config/strongmail-client.conf | cut -d, -f1 | cut -d= -f2 | sort | uniq`

export PGPASSWORD=$PGPASSWORD
/data1/message_studio/thirdparty/pgsql/bin/psql -U postgres -c "COPY (select ip_address from strongmail_eas_server) TO '/tmp/eas_servers'" > /dev/null

EASSERVERS=`cat /tmp/eas_servers`

Prompt()
{
   echo "\
------------------------------------------------------------------------------------------
$1
------------------------------------------------------------------------------------------"
}

UsageEx()
{
   (
    exec 1>&2

    if [ $# -ge 1 ]
    then
       Prompt "ERROR: $1";
    fi
	Prompt "\
	Usage:
	trace_message.sh -t <deployment type> -m <serial or unique identifier>
	deployment type: tier1, tier2, tier3
    ";
	
	)
	
   exit 1;
}

GetCmdlineOptions()
{
while getopts ":t:m:h:" opt
do
   case $opt in
      t ) 
	  type=$OPTARG
	  ;;
      m ) 
	  MID=$OPTARG 
	  ;;  
      h )
	  shift
	  UsageEx;
	  ;;
      * )
	  echo "Invalid option:[$option_str]"
	  exit 1
	  ;;
   esac
done

if [ -z "$type" -a -z "$MID" ]
then
	UsageEx "You must enter the parameters";
fi
}

tier1_search() 
{
echo "searching appserver log..."
echo "###############################################################################################"
#grep $MID $AppServerLog
awk '/'"$MID"'/ {flag=1;next} /'"$MID"'/{flag=0} flag {print}' $AppServerLog
echo "###############################################################################################"

echo "searching db files..."
echo "###############################################################################################"
for f in "${DBFile[@]}"; do grep $MID "$f"; done
echo "###############################################################################################"

echo "searching success logs..."
echo "###############################################################################################"
grep $MID $SuccessLOG
grep $MID $SuccessLOG.processed-$Today
echo "###############################################################################################"

echo "searching retry failed logs..."
echo "###############################################################################################"
grep $MID $RetryLOG
grep $MID $RetryLOG.processed-$Today
echo "###############################################################################################"

echo "searching bcc success logs..."
echo "###############################################################################################"
grep $MID $BCCSuccessLOG
grep $MID $BCCSuccessLOG.processed-$Today
echo "###############################################################################################"

echo "searching bcc retry failed logs..."
echo "###############################################################################################"
grep $MID $BCCRetryLOG
grep $MID $BCCRetryLOG.processed-$Today
echo "###############################################################################################"
}


tier2_search() 
{ 
echo "searching appserver log..."
echo "###############################################################################################"
awk '/'"$MID"'/ {flag=1;next} /'"$MID"'/{flag=0} flag {print}' $AppServerLog
echo "###############################################################################################"

echo "searching db files..."
echo "###############################################################################################"
for f in "${DBFile[@]}"; do grep "${i}" "$f"; done
echo "###############################################################################################"

echo "searching success logs..."
echo "###############################################################################################"
for h in "${MTASERVERS[@]}"; do ssh root@"$h" "grep $MID $SuccessLOG.processed-$Today" && "grep $MID $SuccessLOG"; done
echo "###############################################################################################"

echo "searching retry failed logs..."
echo "###############################################################################################"
for h in "${MTASERVERS[@]}"; do ssh root@"$h" "grep $MID $RetryLOG.processed-$Today" && "grep $MID $RetryLOG"; done
echo "###############################################################################################"

echo "searching bcc success logs..."
echo "###############################################################################################"
for h in "${MTASERVERS[@]}"; do ssh root@"$h" "grep $MID $BCCSuccessLOG.processed-$Today" && "grep $MID $BCCSuccessLOG"; done
echo "###############################################################################################"

echo "searching bcc retry failed logs..."
echo "###############################################################################################"
for h in "${MTASERVERS[@]}"; do ssh root@"$h" "grep $MID $BCCRetryLOG.processed-$Today" && "grep $MID $BCCRetryLOG"; done
echo "###############################################################################################"
}

tier3_search()
{
for s in "${EASSERVERS[@]}"; do MTAHOSTS=$(ssh root@"$s" "grep HostName /data1/strongmail/config/strongmail-client.conf | cut -d, -f1 | cut -d= -f2 | sort | uniq"); done

echo "searching appserver log..."
echo "###############################################################################################"
awk '/'"$MID"'/ {flag=1;next} /'"$MID"'/{flag=0} flag {print}' $AppServerLog
echo "###############################################################################################"

echo "searching db files..."
echo "###############################################################################################"
for s in "${EASSERVERS[@]}"; do ssh root@"$s" "for f in "${DBFile[@]}"; do grep $MID "$f"; done"; done
echo "###############################################################################################"

echo "searching success logs..."
echo "###############################################################################################"
for h in "${MTAHOSTS[@]}"; do ssh root@"$h" "grep $MID $SuccessLOG.processed-$Today" && "grep $MID $SuccessLOG"; done
echo "###############################################################################################"

echo "searching retry failed logs..."
echo "###############################################################################################"
for h in "${MTAHOSTS[@]}"; do ssh root@"$h" "grep $MID $RetryLOG.processed-$Today" && "grep $MID $RetryLOG"; done
echo "###############################################################################################"

echo "searching bcc success logs..."
echo "###############################################################################################"
for h in "${MTAHOSTS[@]}"; do ssh root@"$h" "grep $MID $BCCSuccessLOG.processed-$Today" && "grep $MID $BCCSuccessLOG"; done
echo "###############################################################################################"

echo "searching bcc retry failed logs..."
echo "###############################################################################################"
for h in "${MTAHOSTS[@]}"; do ssh root@"$h" "grep $MID $BCCRetryLOG.processed-$Today" && "grep $MID $BCCRetryLOG"; done
echo "###############################################################################################"

}

setSSHPassword2()
{
echo "copying ssh key pair to MTA Servers..."
echo "###############################################################################################"
ssh-keygen
for h in "${MTASERVERS[@]}"; do ssh-copy-id -i ~/.ssh/id_rsa.pub "$h"; echo "copied to "$h" completed"; done
}

setSSHPassword3() 
{
echo "generating ssh key pair..."
echo "###############################################################################################"
ssh-keygen

echo "copying ssh key pair to EAS Servers..."
echo "###############################################################################################"
for e in "${EASSERVERS[@]}"; do ssh-copy-id -i ~/.ssh/id_rsa.pub "$e"; echo "copied to "$e" completed"; done

echo "copying ssh key pair to MTA Servers..."
echo "###############################################################################################"
for s in "${EASSERVERS[@]}"; do MTAHOSTS=$(ssh root@"$s" "grep HostName /data1/strongmail/config/strongmail-client.conf | cut -d, -f1 | cut -d= -f2 | sort | uniq"); done
for k in "${MTAHOSTS[@]}"; do ssh-copy-id -i ~/.ssh/id_rsa.pub "$k"; echo "copied to "$k" completed"; done
}

main()
{
GetCmdlineOptions "$@"

if [ $type == "tier1" ]
then
    tier1_search 

   elif [ $type == "tier2" ]
then
    while true; do
    read -p "Do you wish to set SSH password free (y/n)? " yn
    case $yn in
        [Yy]* ) setSSHPassword2; tier2_search; break;;
        [Nn]* ) tier2_search; break;;
        * ) echo "Please answer yes or no.";;
    esac
    done

   elif [ $type == "tier3" ]
then
    while true; do
    read -p "Do you wish to set SSH password free (y/n)? " yn
    case $yn in
        [Yy]* ) setSSHPassword3; tier3_search; break;;
        [Nn]* ) tier3_search; break;;
        * ) echo "Please answer yes or no.";;
    esac
    done
fi
}

main "$@"
