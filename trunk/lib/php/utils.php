<?php

function HTTPDownload($host, $files, $ldir)
{
 foreach($files AS $args) {
  $path = $args['infile'];
  BreakPath($path,$dir,$file);
  echo "Downloading $host$dir$file ... ";
  if(!@copy($host.$dir.$file,$ldir.$file)) {
    $errors= error_get_last();
    echo $errors['type']." : ".$errors['message'].PHP_EOL;
  } else {
    echo "$file copied from $site$dir into $ldir".PHP_EOL;
  }
 }
 return 0;
} // download

function BreakPath($path, &$dir, &$file)
{
  $rpos = strrpos($path,'/');
  if($rpos !== FALSE) {
	$dir = substr($path,0,$rpos+1);
	$file = substr($path,$rpos+1);
   } else {
	$dir = "";
	$file = $path;
   }
   return 0;
}


/**
 * Copy a file, or recursively copy a folder and its contents
 *
 * @author      Aidan Lister <aidan@php.net>
 * @version     1.0.1
 * @link        http://aidanlister.com/repos/v/function.copyr.php
 * @param       string   $source    Source path
 * @param       string   $dest      Destination path
 * @return      bool     Returns TRUE on success, FALSE on failure
 */
function copyr($source, $dest)
{
    // Check for symlinks
    if (is_link($source)) {
        return symlink(readlink($source), $dest);
    }

    // Simple copy for a file
    if (is_file($source)) {
        return copy($source, $dest);
    }

    // Make destination directory
    if (!is_dir($dest)) {
        mkdir($dest);
    }

    // Loop through the folder
    $dir = dir($source);
    while (false !== $entry = $dir->read()) {
        // Skip pointers
        if ($entry == '.' || $entry == '..') {
            continue;
        }

        // Deep copy directories
        copyr("$source/$entry", "$dest/$entry");
    }

    // Clean up
    $dir->close();
    return true;
}

function GetDirFiles($dir,$pattern)
{
 if(!is_dir($dir)) {
  echo "$dir not a directory".PHP_EOL;
  return 1;
 }

 $dh = opendir($dir);
 while (($file = readdir($dh)) !== false) {
  if($file == '.' || $file == '..') continue;
  $files[] = $file;
 }
 sort($files);
 closedir($dh);
 return $files; 
}


?>
