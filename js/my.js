var timer_id
function showNotice(id){
	$("#"+id).
		show("blind",{easing:"easeOutBounce"},1000,function(){
			timer_id = setTimeout( function(){
				if($("#"+id).is(":visible")){
					$("#"+id).hide("blind",{easing:"easeOutExpo"},1000)
				}
			},
			15000)
		});
}

function hideNotice(id){
	$("#"+id).hide("blind",{easing:"easeOutExpo"},1000)
    clearTimeout(timer_id)
}

function onKeyUp(e){
	if(document.forms['trans'].elements['input'].disabled){ return;}

	if(e.keyCode==27){ // 27:ESC
		deleteChildElements('disp_parent');
	}
};

function deleteChildElements(id){
	var elem=document.getElementById(id);
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

// my own fadeOut
function fadeOut(i,n){
	var id="notice_"+String(i);
	if(n<0){
		var elem=document.getElementById(id);
		pnode=elem.parentNode;
		pnode.removeChild(elem);
		return;
	}
	$("#"+id).css({opacity:n/10.0});
	setTimeout(function(){fadeOut(i,n-1)},50);
}

function notice(i,word){
	var id="notice_"+String(i);
	var new_span = document.createElement("span");
	new_span.innerHTML = word;
	new_span.id = id;
	document.body.appendChild(new_span);

	var prop = {
		position: "absolute",
		//top : ($(window).scrollTop()+$(window).height()-75)+"px",
		top : ($(window).scrollTop()+25)+"px",
		left: (window.innerWidth*3/5)+"px",
		border: "3px solid yellow",
		padding: "10px",
		backgroundColor:"#ffffcc",
		fontWeight: "bold",
	}

	$("#"+id).css(prop);

	$("#"+id).show();
	setTimeout(
		function(){
			//$("#"+id).hide("highlight",{},1000)
			$("#"+id).fadeOut(function(){
				var elem=document.getElementById(id);
				pnode=elem.parentNode;
				pnode.removeChild(elem);
			});
		},
		1000
	);
	//fadeOut(i,10);
}

function makeQueries(){

	document.forms['trans'].elements['input'].disabled=true;

	if(!document.forms['trans'].elements['increment'].checked){
		deleteChildElements("disp_parent");
	}

	var text = document.forms['trans'].elements['text'].value;
	var words = [];
	var splits=text.split('\n')
	for(var i=0;i<splits.length;++i){
		if(splits[i]==""){
		}else{
			words.push(splits[i]);
		}
	}
	var field = document.getElementById('disp_parent');

	var ncur=0;
	for (var i=0;i<field.childNodes.length;i++){
		id=parseInt(field.childNodes[i].id.split('_')[1])+1;
		if(ncur<id){ ncur=id; }
	}

	var site="";
	site_elem=document.forms['trans'].elements['site'];
	for(var j=0;j<site_elem.length;j++){
		if(site_elem[j].checked){
			site=site_elem[j].value;
			break;
		}
	}

	var new_div= document.createElement("div");
	new_div.id = "loader_image";
	var new_p= document.createElement("p");
	new_div.appendChild(new_p);

	document.body.insertBefore(new_div,field);
	startAnimation(site);

    if(localStorage.transatonce){
	    var list_to_cache = [];
        var cached_list = localStorage.transatonce.split("\n")
        for(var i=0;i<words.length;i++){
            if($.inArray(words[i],cached_list)==-1){
                list_to_cache.push(words[i]);
            }
        }

        var str_to_cache = list_to_cache.join("\n");

        try{
            localStorage.transatonce += ("\n"+str_to_cache);
        } catch (e) {
            if (e.code === DOMException.QUOTA_EXCEEDED_ERR ||
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') {

                var cached_length = 0;
                var cached_1st_index = 0;

                for(var i=0;i<cached_list.length-1;i++){
                    cached_length += cached_list[i].length;
                    cached_length ++;
                    if(cached_length>str_to_cache.length){
                        cached_1st_index = i;
                        break;
                    }
                }

                localStorage.transatonce =
                    cached_list.slice(cached_1st_index+1).join("\n")+"\n"+str_to_cache;

            } else {
                alert('エラーが発生しました.');
            }
        }

    }else{
        localStorage.transatonce = words.join("\n");
    }

	query(0,words,ncur,site);
}

function deleteDiv(id){
	var par=document.getElementById("disp_parent");
	par.removeChild(document.getElementById(id));
}

function query(i,words,ncur,site){

	//if(i>0) ripple(230,i%3);
	if(document.forms['trans'].elements['notice'].checked){
		if(i>0){
			if(words[i-1]!="") notice(i,words[i-1]);
		}
	}

	if(i>0){
		var prev_id = "disp_"+String(i-1+ncur);
		var prev_div = document.getElementById(prev_id);

		var new_input=document.createElement("input");
		new_input.type="button";
		new_input.value="Close";

		// XXX: addEventListener and onclick property not working.
		//new_input.addEventListener("click",function(){deleteDiv(prev_id);});
		//new_input.onclick="deleteDiv("+prev_id+")";
		new_input.setAttribute("onClick","deleteDiv('"+prev_id+"')");

		var new_span=document.createElement("span");
		new_span.innerHTML="&nbsp;&nbsp;";

		if(prev_div.childNodes.length>4){
			prev_div.insertBefore(new_input,prev_div.childNodes[4]);
			prev_div.insertBefore(new_span,prev_div.childNodes[4]);
		}else{
			if(prev_div.firstChild){
				prev_div.insertBefore(new_span,prev_div.firstChild);
				prev_div.insertBefore(new_input,prev_div.firstChild);
			}
		}
	}

	if(i>=words.length){
		document.forms['trans'].elements['input'].disabled=false;
		stopAnimation();
		document.body.removeChild(document.getElementById("loader_image"));
		return;
	}

	var tag_div = "disp_"+String(i+ncur);
	var new_div = document.createElement("div");
	new_div.id=tag_div;

	parent=document.getElementById('disp_parent');
	if(parent.firstChild){
		parent.insertBefore(new_div,parent.firstChild);
	}else{
		parent.appendChild(new_div);
	}

	$('div#'+tag_div).load(
		'/trans',
		{word:words[i],site:site},
		function(responseText, status, XMLHttpRequest){
			query(i+1,words,ncur,site);
		}
	);
}

function flushCacheEntries(){
	var r = confirm("保存された単語を消去しますか?");
	if (r == true) {
        localStorage.clear();
	} else {

	}
}

function count(){
	var text = document.forms['trans'].elements['text'].value;
	if( text.split('\n').length > 50 ) {
		alert("Too many words to process!\n");
	}
}

function explain(name){
	if(name=="increment"){
		if(document.forms['trans'].elements['increment'].checked){
			//alert("このボタンをチェックすることにより、前回の結果に続けて表示していきます。");
			showNotice("incr_notice");
		}
	}else if(name=="notice")
		if(!document.forms['trans'].elements['notice'].checked){
			alert("noticeボタンのチェックを外すと、処理が終わった通知が出なくなります。");
	}
}

function ask(){

	if(document.forms['trans'].elements['input'].disabled){ return; }
	if(!document.forms['trans'].elements['increment'].checked){ return; }

	var text = document.forms['trans'].elements['text'].value;
	if( text == "" ){ return; }

	/*
	var r = confirm("テキストボックスの内容を消去しますか?");
	if (r == true) {
		document.forms['trans'].elements['text'].value="";
	} else {
		
	}
	*/
	document.forms['trans'].elements['text'].value="";

}

function loadCache(){
    var text_elem = document.forms['trans'].elements['text'];
    if(localStorage.transatonce){
        text_elem.value = localStorage.transatonce;
    }
}

function clearBox(){
	document.forms['trans'].elements['text'].value="";
}

