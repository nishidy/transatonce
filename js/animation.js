var cSpeed=3;
var cWidth=40;
var cHeight=43;
var cTotalFrames=29;
var cFrameWidth=40;
	
var cImageTimeout=false;
var cIndex=0;
var cXpos=0;
var cPreloaderTimeout=false;
var SECONDS_BETWEEN_FRAMES=0;

var loadingImages = {"alc":"images/sprites_alc.gif",
					 "goo":"images/sprites_goo.gif",
					 "longman":"images/sprites_longman.gif"};

function continueAnimation(){
	
	cXpos += cFrameWidth;
	//increase the index so we know which frame of our animation we are currently on
	cIndex += 1;
	 
	//if our cIndex is higher than our total number of frames, we're at the end and should restart
	if (cIndex >= cTotalFrames) {
		cXpos =0;
		cIndex=0;
	}
	
	if(document.getElementById('loader_image'))
		document.getElementById('loader_image').style.backgroundPosition=(-cXpos)+'px 0';
	
	cPreloaderTimeout=setTimeout('continueAnimation()', SECONDS_BETWEEN_FRAMES*1000);
}

function startAnimation(site){
	
	document.getElementById('loader_image').style.backgroundImage='url('+loadingImages[site]+')';
	document.getElementById('loader_image').style.width=cWidth+'px';
	document.getElementById('loader_image').style.height=cHeight+'px';
	
	//FPS = Math.round(100/(maxSpeed+2-speed));
	FPS = Math.round(100/cSpeed);
	SECONDS_BETWEEN_FRAMES = 1 / FPS;
	
	cPreloaderTimeout=setTimeout('continueAnimation()', SECONDS_BETWEEN_FRAMES/1000);
	
}

function stopAnimation(){//stops animation
	clearTimeout(cPreloaderTimeout);
	cPreloaderTimeout=false;
}

function imageLoader(s)
{
	for(var key in loadingImages){
		genImage = new Image();
		genImage.onerror=new Function('alert(\'Could not load the image\')');
		genImage.src=loadingImages[key];
	}
}
