window.log = function(){
  log.history = log.history || [];  
  log.history.push(arguments);
  arguments.callee = arguments.callee.caller;  
  if(this.console) console.log( Array.prototype.slice.call(arguments) );
};
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();)b[a]=b[a]||c})(window.console=window.console||{});

//This is incredibly verbose code required by Django to satisfy CSRF protection for Ajax. We should probably save this somewhere that's easy to get to.
$(document).ajaxSend(function(event,xhr,settings){function getCookie(name){var cookieValue=null;if(document.cookie&&document.cookie!=''){var cookies=document.cookie.split(';');for(var i=0;i<cookies.length;i++){var cookie=jQuery.trim(cookies[i]);if(cookie.substring(0,name.length+1)==(name+'=')){cookieValue=decodeURIComponent(cookie.substring(name.length+1));break;}}}return cookieValue;}function sameOrigin(url){var host=document.location.host;var protocol=document.location.protocol;var sr_origin='//'+host;var origin=protocol+sr_origin;return(url==origin||url.slice(0,origin.length+1)==origin+'/')||(url==sr_origin||url.slice(0,sr_origin.length+1)==sr_origin+'/')||!(/^(\/\/|http:|https:).*/.test(url));}function safeMethod(method){return(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));}if(!safeMethod(settings.type)&&sameOrigin(settings.url)){xhr.setRequestHeader("X-CSRFToken",getCookie('csrftoken'));}});