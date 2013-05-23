<?php

/**
 * ask for an axiom (annotation or subclass axiom) in which the IP hasn't answered, and needs answers [1<5] or random
 * present a question: do you agree that [term] [has definition|is a type of] [annotation|class expression]
 * present radio box / 3 buttons : yes, no, i don't know
 * present a comment box
 * store the result with IP address
*/
?>
<html>
<head>
 <title>Ontology Evaluator</title>
</head>
<body>
<h3>ontology evaluator: SIO</h3>
<?php
 require('backend.php');
 $type_list = array("annotation","subclass");
 $answer_list = array("yes","no","i don't know");
 
 $o = new stdClass();
 if($testing == true) {
	$o->type = "annotation";
	$o->term_id = "SIO_000001";
	$o->term = "protein";
	$o->text = "a protein is a linear ...";
 }
 
 // validate results and send to backend
 if(isset($_REQUEST) and isset($_REQUEST['answer'])) {
	$o->ip = $_SERVER['REMOTE_ADDR'];
	// type check
	if(!in_array($_REQUEST['type'], $type_list))
		exit;
	}
	$o->type = $_REQUEST['type'];
	
	// id check SIO_123456
	preg_match("/(SIO_[0-9]{6})/",$_REQUEST['term_id'],$m);
	if(!isset($m[1])) {
		exit;
	}
	$o->term_id = $m[1];
	
	// answer check
	if(!in_array($_REQUEST['answer'], $answer_list)) {
		exit;
	}
	
	$o->comment = $_REQUEST['comment'];
	
	$o->submit();
  }

 $question = "Do you agree that ";
 if($o->type == "annotation") {
	$question .= " a reasonable definition for '$o->term' is '$o->text' ?";
 } else {
	$question .= " $o->term is a type of $o->text ?";
 }
 echo $question;

?>
 <form id="submit" method="post">
	<input name="type" type="hidden" value="<?php echo $o->type;?>"/>
	<input name="term_id" type="hidden" value="<?php echo $o->term_id;?>"/>
	<input name="text" type="hidden" value="<?php echo $o->text;?>"/>
<?php foreach($answer_list AS $answer) { 
	echo '<input name="answer" type="submit" value="'.$answer.'"><br>';
}?>
	<br><br>
	if "no" or "i don't know", please comment:<br>
	<textarea name="comment"></textarea>
 </form>
</body>
</html>