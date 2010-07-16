
<?php include('header.php');?>
 <script type="text/javascript" language="javascript" src="api/dt/media/js/jquery.js"></script> 
 <script type="text/javascript" language="javascript" src="api/dt/media/js/jquery.dataTables.js"></script> 
 <script type="text/javascript">
 
 $(document).ready(function() {
	$('#example').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
		"sAjaxSource": "bin/dataset_fetch.php",
		"sPaginationType": "full_numbers",
		"aoColumns": [
			/* expand */ { "bSortable": false },
			/* prefix */ null,
			/* url */    {"bVisible": false},
			/* title */  {"bSortable": false},
			/* description */ { "bSortable": false, "bVisible": false }
		],
	} );
} );

 </script>
<div id="trans-box">
<h1>Life Science Dataset Registry</h1>

<div id="dynamic"> 
<table cellpadding="0" cellspacing="0" border="0" class="display" id="example"> 
	<thead> 
		<tr> 
			<th width="0"></th> 
			<th width="15%">prefix</th> 
			<th width="0"></th> 
			<th width="85%">title</th> 
			<th width="0">description</th> 
		</tr> 
	</thead> 
	<tbody>
		<tr> 
			<td colspan="5" class="dataTables_empty">Loading data from server</td> 
		</tr> 
	</tbody> 
</table> 
</div>

<br/>
<br/>
</div>
<?php include('footer.php');?>