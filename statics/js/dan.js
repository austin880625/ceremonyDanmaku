var user_id="";
var ws;
var waiting=0;
var is_lock=0;
var inter_ping,inter_clearq;
var input_msg="寫下你的祝福或讚賞(or吐槽";
var danmaku_queue=Array();
//var gettime=0;

function checkAvailability(){
    if(waiting<=1){
        waiting=0;
        is_lock=0;
        $("#danmaku_content").removeAttr("disabled");
        $("#danmaku_content").attr("placeholder",input_msg);
        $("#send").removeAttr("disabled");
    }
    else{
        waiting--;
        setTimeout(checkAvailability,1000);
        $("#danmaku_content").attr("placeholder","請再等待"+waiting.toString()+"秒");
    }
}

function react(d){
    if(d=="L"){
        console.log("not logged in");
    }else if(d=="R"){
        console.log("not rigistered");
    }else if(d=="N"){
        $("#danmaku_content").attr("disabled","disabled");
        $("#send").attr("disabled","disabled");
        $("#danmaku_content").attr("placeholder","彈幕未開放");
    }else if(d<=0){
        $("#danmaku_content").removeAttr("disabled");
        $("#danmaku_content").attr("placeholder",input_msg);
        $("#send").removeAttr("disabled");
    }else {
        $("#danmaku_content").attr("disabled","disabled");
        $("#send").attr("disabled","disabled");
        waiting=d;
        if(is_lock==0){is_lock=1;setTimeout(checkAvailability,1000);}
        $("#danmaku_content").attr("placeholder","請再等待"+waiting+"秒");
    }
}

function ping_server(){
    ws.send("ping");
}

function start_ws(server_url){
    ws = new WebSocket("ws://"+server_url+"/Pusheen");
    ws.onopen = function(){

    }
    clearInterval(inter_ping);
    inter_ping=setInterval(ping_server,40000);
    ws.onmessage = function(e){
        var data=JSON.parse(e.data);
        if(data.state=="connection established."){
            console.log("connection established.");
        }else if(data.state=="pong"){
            return ;
        }else if(data.state=="dan"){
            var len=0,i;
            for(i=0;i<data.content.length;i++){
                x=data.content.charCodeAt(i);
                if(x<=0x7f){
                    len++;
                }else{
                    len+=2;
                }
                if(len>=50)break;
            }
            var line=document.createElement("div");
            var text=document.createTextNode(data.user+"："+data.content.slice(0,i));
            line.appendChild(text);
            danmaku_queue.push(line);
            var ele=document.getElementById("recent_danmaku");
            ele.appendChild(line);
            $("#recent_danmaku").animate({scrollTop:ele.scrollHeight},150);
        }else if(data.state=="upd"){
            if(data.dan!=null){
                if(data.dan==0){
                    $("#danmaku_content").val("");
                    $("#danmaku_content").attr("disabled","disabled");
                    $("#send").attr("disabled","disabled");
                    $("#danmaku_content").attr("placeholder","彈幕未開放");
                }
                else{
                    $("#danmaku_content").removeAttr("disabled");
                    $("#danmaku_content").attr("placeholder",input_msg);
                    $("#send").removeAttr("disabled");
                    waiting=0;
                }
            }
            if(data.program!=null){
                $("#current_program").text(data.program);
            }
            //alert(data.state);
            //responded=1;
        }else{
            react(data.state);
        }
    }
    ws.onclose = function(){
        setTimeout(function(){start_ws(server_url);},5000);
    }
}

function checkLoginState(){
    FB.getLoginStatus(function(response) {
        if(response.status=='connected'){
            console.log('logged in.');
            var accessToken=response.authResponse.accessToken;
            user_id=response.authResponse.userID;
            $.ajax({
                type:"post",
                url:"/register",
                async:false,
                data:{'user_fb_token':accessToken,'user_id':user_id},
                success:function(d){
                    //alert(d);
                    if(d=="success"){
                        $("#danmaku_content").text("");
                    }else{
                        console.log("error");
                    }
                },
                error:function(data){},
            });
            $("#send_form").show();
            $("#danmaku_content").attr("placeholder",input_msg);
            $(".fb-login-button").hide();
            var server_url=window.location.hostname+":"+window.location.port;
            if("WebSocket" in window && ws==null){
                start_ws(server_url);
            }
        }

    });

}

function logout(){
    FB.logout(function(){console.log("logged out.")});
}

function clearq(){
    while(danmaku_queue.length>10){
        var ele=document.getElementById("recent_danmaku");
        ele.removeChild(danmaku_queue[0]);
        danmaku_queue.shift();
    }
}
$(document).ready(function(){
    inter_clearq=setInterval(clearq,5000);

    $("#send").click(function(){
        if($("#danmaku_content").val()==""){
            alert("請輸入內容");
            return ;
        }
        var len=0,i;
        var content=$("#danmaku_content").val();
        for(i=0;i<content.length;i++){
            x=content.charCodeAt(i);
            if(x<=0x7f){
                len++;
            }else{
                len+=2;
            }
            if(len>=50)break;
        }
        danmaku_content={
            //"user_id":user_id,
            "content":content.slice(0,i),
        };
        $("#danmaku_content").val("");

        if("WebSocket" in window){
            if(ws==null){var server_url=window.location.hostname+":"+window.location.port;start_ws(server_url);}
            ws.send(JSON.stringify(danmaku_content));
        }else{
            $.ajax({
                type:"post",
                url:"/senddanmaku",
                data:danmaku_content,
                success:function(d){
                    react(d);
                },
                error:function(data){},
            });
        }
    });
    $("#danmaku_content").keypress(function(e){
      if(e.keyCode==13)
      $("#send").click();
    });
    $("#danmaku_content").focus(function(){
      window.scrollTo(0,document.body.scrollHeight);
    });

    $(window).focus(function(){
        if(user_id!=""&&user_id!=null){
            if(ws==null){
                $.ajax({
                    type:"get",
                    url:"/senddanmaku",
                    success:function(d){
                        waiting=d;
                        $("#danmaku_content").attr("disabled","disabled");
                        $("#send").attr("disabled","disabled");
                        checkAvailability();
                        //console.log("YEE");
                    },
                });
            }else{
                ws.send(JSON.stringify({"content":""}))
            }
        }
    });
});
