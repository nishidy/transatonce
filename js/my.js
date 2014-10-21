
function deleteElement(id){
	elem=document.getElementById(id);
	firstChild=elem.firstChild;
	if(firstChild==null) return;
	while(firstChild.nextSibling){
		elem.removeChild(firstChild.nextSibling);
	}
	elem.removeChild(firstChild);
}

function makeEachQuery(){
	deleteElement("disp_parent");

	var text = document.forms['trans'].elements['text'].value;
	var artext = text.split('\n');
	var field = document.getElementById('disp_parent');

	query(0,artext.length,field,artext);
}

function query(i,num,field,artext){
	if(i==num) return;
	console.log(i,artext[i]);

	tag_div = "disp"+String(i);
	new_div = document.createElement("div");
	new_div.id=tag_div;
	field.appendChild(new_div);

	$('div#'+tag_div).load(
			'/trans',
			{words:artext[i]},
			function(a,b,c){if(i<num) query(i+1,num,field,artext)}
	);
}

function count(){
	var text = document.forms['trans'].elements['text'].value;
	if( text.split('\n').length > 50 ) {
		alert("Too many words to process!\n");
	}
}

