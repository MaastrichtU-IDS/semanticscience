<?php
$instance_file = "bio2rdf-instances.tab";
$config_file   = "bio2rdf-virtuoso";
$target_dir    = "/bio2rdf";

$ns = $argv[1];
$fnx = $argv[2];
$server = $argv[3];


if($argc < 3 || !in_array($fnx,array("create","start","stop","config"))) {
 echo "$argv[0] [all|ns] [create|start|stop|config] [server]".PHP_EOL;
 exit;
}

GetInstancesFromFile($instances);
if($ns != "all") {
  if(!isset($instances[$ns])) {
    echo "Fist add the $ns entry to $instance_file".PHP_EOL;
    exit;
  }
  $list[$ns] = $instances[$ns];
} else $list = $instances;


$buf ='';
foreach($list AS $n => $i) 
{
  if($ns == 'all' && ($i['server'] != $server)) continue;
  if($fnx == "create") Create($i);
  else if($fnx == "start") Start($i);
  else if($fnx == "stop") Stop($i);
  else if($fnx == "config") $buf .= Config($i);
  if($ns != 'all') break;
}
if($buf) file_put_contents($config_file,$buf);




function Create($instance)
{
 global $target_dir;

 $ns = $instance['ns'];
 echo "Creating $ns ...";
 
 // create the directory if it doesn't exist
 if(!is_dir("$target_dir/instance/$ns")) {
  system("mkdir -p $target_dir/instance/$ns/bin");
  system("mkdir -p $target_dir/instance/$ns/db");
 }
 
 // copy the executable and the config file
 system("cp -f default/bin/v-default $target_dir/instance/$ns/bin/v-$ns"); // copy the v-default to v-$ns

 // now read in the virtuoso file and modify the db, www port and isql port
 $inifile = "default/bin/virtuoso.ini"; 
 $buf = file_get_contents($inifile);
 if($buf === FALSE) {
  echo "Unable to read $inifile";
  exit;
 }
 $v = str_replace( 
	array(  "virtuoso.db", "10000", "8000", "http://bio2rdf.org/ns"), 
	array(  "/bio2rdf/virtuoso.db/$ns.virtuoso.db", 
		$instance['isql_port'], 
		$instance['www_port'],
		"http://bio2rdf.org/$ns"
	), 
	$buf
 );
 file_put_contents("$target_dir/instance/$ns/bin/virtuoso.ini",$v);
 echo "done.".PHP_EOL;

 return 0;
}

function Stop($instance)
{
  $ns = $instance['ns'];

  system("pgrep v-$ns");
  system("sudo pkill v-$ns"); 
}

function Start($instance)
{
  global $target_dir;

  Stop($instance);

  // start it up
  $ns = $instance['ns'];
  $cmd = "cd $target_dir/instance/$ns/bin/;sudo ./v-$ns &"; 
  system($cmd);
  system("pgrep v-$ns");
}



function GetInstancesFromFile(&$instances)
{
 global $instance_file;
 $fp = fopen($instance_file,"r");
 while($l = fgets($fp)) {
  $a = explode("\t",trim($l));
  $i["isql_port"] = $a[0];
  $i["www_port"] = $a[1];
  $i["server"] = $a[2];
  $i["ns"] = $a[3];
  $instances[$i['ns']] = $i;
 }
 fclose($fp);
}

// file format
// isql_port\twww_port\tname\tserver\n
function WriteInstancesToFile($instances)
{
 global $instance_file;

 $buf = '';
 foreach($instances AS $ns => $i) {
  $buf .= $i["isql_port"]."\t".$i["www_port"]."\t".$i["server"]."\t".$i["ns"]."\n";
 }
 file_put_contents($instance_file,$buf);
 return 0;
}

function GetNextInstance(&$instance)
{
 GetInstancesFromFile($instances);
 // the ports are ordered, so get the last one
 $i = $instance = end($instances);
 $instance["isql_port"] ++;
 $instance["www_port"] ++; 
}


function Config(&$instance)
{
$ns = $instance['ns'];
$port = $instance['www_port'];

$buf = '<VirtualHost *:80>
  ServerName  cu.'.$ns.'.bio2rdf.org  
  ServerAlias '.$ns.'.bio2rdf.org  
  ProxyRequests Off
  <Proxy *>
    Order deny,allow
    Allow from all
  </Proxy>
  ProxyPass / http://cu.'.$ns.'.bio2rdf.org:'.$port.'/
  ProxyPassReverse / http://cu.'.$ns.'.bio2rdf.org:'.$port.'/
</VirtualHost>
';
 return $buf;
}
?>
