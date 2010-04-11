<?php
class MyXmlWriter{
var $xml;
var $indent;
var $stack = array();
function XmlWriter($indent = '  ') {
$this->indent = $indent;
$this->xml = '<?xml version="1.0" encoding="utf-8"?>'."\n";
}
function _indent() {
for ($i = 0, $j = count($this->stack); $i < $j; $i++) {
    $this->xml .= $this->indent;
}
}
function push($element, $attributes = array()) {
$this->_indent();
$this->xml .= '<'.$element;
foreach ($attributes as $key => $value) {
    $this->xml .= ' '.$key.'="'.htmlentities($value).'"';
}
$this->xml .= ">\n";
$this->stack[] = $element;
}
function element($element, $content, $attributes = array()) {
$this->_indent();
$this->xml .= '<'.$element;
foreach ($attributes as $key => $value) {
    $this->xml .= ' '.$key.'="'.htmlentities($value).'"';
}
$this->xml .= '>'.htmlentities($content).'</'.$element.'>'."\n";
}
function emptyelement($element, $attributes = array()) {
$this->_indent();
$this->xml .= '<'.$element;
foreach ($attributes as $key => $value) {
    $this->xml .= ' '.$key.'="'.htmlentities($value).'"';
}
$this->xml .= " />\n";
}
function pop() {
$element = array_pop($this->stack);
$this->_indent();
$this->xml .= "</$element>\n";
}
function getXml() {
return $this->xml;
}
}

?>
