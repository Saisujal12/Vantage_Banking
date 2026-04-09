function toggleMenu(){
let menu = document.getElementById("homeMenu");

if(menu.style.display === "block"){
menu.style.display = "none";
}else{
menu.style.display = "block";
}
}

function createAccount(){
document.getElementById("msg").innerHTML =
"✅ Account Created Successfully! Please Login.";
return false;
}
