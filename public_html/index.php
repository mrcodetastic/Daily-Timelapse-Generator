<!DOCTYPE html>
<html lang="en"> 
<head>
	<meta charset="utf-8">
	<title>Timelapse</title>
	<meta name="description" content="Timelapse">
	<meta name="author" content="Nobody" />	
	
	<link href="https://fonts.googleapis.com/css?family=Oleo+Script" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Acme" rel="stylesheet">

		
	<style>
		body {
		  margin: 0;
		  background: #000; 
		}
		
		 .header
		{
			text-align: center;
			margin: .5em;
			padding: .2em;
			/* font-family: Tahoma, Geneva, sans-serif; */
			font-family: 'Oleo Script', cursive;
			font-size: 1em;
			color: #FFF;

			background-color: rgba(255, 255, 255, 0.5); 
			border-radius: .25em;		 
	   }
	   

		video { 
			position: fixed;
			top: 50%;
			left: 50%;
			min-width: 100%;
			min-height: 100%;
			width: auto;
			height: auto;
			z-index: -100;
			transform: translateX(-50%) translateY(-50%);
			background-size: cover;
			transition: 2s opacity;
		}
		

	</style>
</head>
<body> 

<div class="header">Timelapse from XXXX yesterday: <?php readfile('last_updated.txt'); ?></div>

<video poster="loading.jpg" playsinline autoplay muted loop>
  <source src="<?php readfile('latest_timelapse_file.txt'); ?>" type="video/mp4">
  Your browser does not support HTML5 video.
</video>

</body> 
</html>
