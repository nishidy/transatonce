
function deleteElement(id){
	elem=document.getElementById(id);
	firstChild=elem.firstChild;
	if(firstChild==null) return;
	while(firstChild.nextSibling){
		elem.removeChild(firstChild.nextSibling);
	}
	elem.removeChild(firstChild);
}

// obsoleted
function ripple(c,k){
	if(c>255) return;
	setTimeout(function(){ripple(c+1,k)},10);
	if(k==0){
		document.bgColor = "#"+c.toString(16)+c.toString(16)+"ff";
	}else if(k==1){
		document.bgColor = "#"+c.toString(16)+"ff"+c.toString(16);
	}else{
		document.bgColor = "#"+"ff"+c.toString(16)+c.toString(16);
	}
}

function vanish(i,n){
	id="notice_"+String(i);
	if(n<0){
		elem=document.getElementById(id);
		pnode=elem.parentNode;
		pnode.removeChild(elem);
		return;
	}
	$("#"+id).css({opacity:n/10.0});
	setTimeout(function(){vanish(i,n-1)},50);
}

function notice(i,word){
	id="notice_"+String(i);
	new_span = document.createElement("span");
	new_span.innerHTML = word;
	new_span.id = id;
	document.body.appendChild(new_span);

	var prop = {
		position: "absolute",
		top : ($(window).scrollTop()+15)+"px",
		left: (window.innerWidth*4/5)+"px",
		border: "3px solid yellow",
		padding: "10px",
		backgroundColor:"#ffffcc",
		fontWeight: "bold",
	}

	$("#"+id).css(prop);
	vanish(i,10);
}


function makeQuery(){

	document.forms['trans'].elements['input'].disabled=true;

	if( ! document.forms['trans'].elements['append'].checked ){
		deleteElement("disp_parent");
	}

	var text = document.forms['trans'].elements['text'].value;
	var artext = text.split('\n');
	var field = document.getElementById('disp_parent');

	ncur = document.getElementById('disp_parent').childNodes.length;

	query(0,artext,ncur);
}

function query(i,artext,ncur){

	//if(i>0) ripple(230,i%3);

	if(document.forms['trans'].elements['notice'].checked){
		if(i>0){
			if(artext[i-1]!="") notice(i,artext[i-1]);
		}
	}

	if(i==artext.length){
		document.forms['trans'].elements['input'].disabled=false;
		return;
	}

	tag_div = "disp_"+String(i+ncur);
	new_div = document.createElement("div");
	new_div.id=tag_div;

	document.getElementById('disp_parent').appendChild(new_div);

	var j;
	for(j=0;j<document.forms['trans'].elements['site'].length;j++){
		if(document.forms['trans'].elements['site'][j].checked){
			site=document.forms['trans'].elements['site'][j].value;
			break;
		}
	}

	$('div#'+tag_div).load(
			'/trans',
			{word:artext[i],site:site},
			function(responseText, status, XMLHttpRequest)
			  {query(i+1,artext,ncur)}
	);
}

function count(){
	var text = document.forms['trans'].elements['text'].value;
	if( text.split('\n').length > 50 ) {
		alert("Too many words to process!\n");
	}
}

