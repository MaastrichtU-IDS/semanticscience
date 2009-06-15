<?php

function HTTPDownload($host, $files, $ldir)
{
 foreach($files AS $args) {
  $path = $args['infile'];
  BreakPath($path,$dir,$file);

  if(!@copy($site.$dir.$file,$ldir.$file)) {
    $errors= error_get_last();
    trigger_error($errors['type'].": ".$errors['message']);
  } else {
    echo "$file copied from $site$dir into $ldir!".PHP_EOL;
  }
 }
 return 0;
} // download

function BreakPath($path, &$dir, &$file)
{
  $rpos = strrpos($path,'/');
  $dir = substr($path,0,$rpos+1);
  $file = substr($path,$rpos+1);
}

?>