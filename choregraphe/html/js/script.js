user_cmd = [];
session = null;
QiSession(connected, disconnected, location.host);

function connected(s) {
    //alert("Session connected");
    session = s;
    //If you want to subscribe so some events (to send info pepper->tablet) call the function here
    session.service("ALMemory").then(function(memory) {
	memory.subscriber("order").then(function(subscriber) {
	    // subscriber.signal is a signal associated to "order"
	    subscriber.signal.connect(function(value) {
		addPlats(value); // ajoute les plats à la commande
	    });
	});
    });

     session.service("ALMemory").then(function(memory) {
	memory.subscriber("end_order").then(function(subscriber) {
	    // subscriber.signal is a signal associated to "order"
	    subscriber.signal.connect(function(value) {
		user_cmd = []; // réinitialise la commande 
	    });
	});
    });
}

function disconnected(error) {
    alert("Session disconnected");
}

function cost(){
    var somme = 0;
    var i;
    for(i = 0; i < user_cmd.length; i++){
	somme += user_cmd[i].price;
    }

    return somme;
}

function addPlats(value){
    var i;
    for(i = 0; i < value.length; i++){
	var value_i = value[i].split(":");
	var commande = {"name" : value_i[1], "qte" : value_i[0], "price" : 0};

	var name = commande.name;
	switch(name.replace(" ", "")){
	case "Reine":
	    commande.price = 4.5;
	    break;
	case "3fromages":
	    commande.price = 5.5;
	    break;
	case "Texane":
	    commande.price = 5;
	    break;
	case "CocaCola":
	    commande.price = 3.75;
	    break;
	case "Théfroid":
	    commande.price = 3.5;
	    break;
	case "Verred'eau":
	    commande.price = 1;
	    break;
	default:
	    commande.price = 1;
	    break;
	}

	commande.price *= parseInt(commande.qte, 10);
	// alert(JSON.stringify(commande));
	user_cmd.push(commande);
    }
}

function validateForm() {
    var menu = document.getElementById("list_pizzas").children;
    var choices = [];
    var nb_pizzas;
    var i;
    
    for(i = 0; i < menu.length; i++){
	nb_pizzas = menu[i].getElementsByTagName("input")[0];
	if(nb_pizzas.value != "0")
	    choices.push(nb_pizzas.value + " : " + menu[i].firstElementChild.innerHTML);
    }

    console.log(choices);

    session.service("ALMemory").then(function (memory) {
	memory.raiseEvent("order", choices);
    });
}

/*
function sendOui(){
    session.service("ALMemory").then(function (memory) {
	memory.raiseEvent("choix", "Oui");
    });
}

function sendNon(){
    session.service("ALMemory").then(function (memory) {
	memory.raiseEvent("choix", "Non");
    });
}
*/

// **********************************************
//              html behaviors
// **********************************************

function updateTextInput(elementId, val){
    elementId += "_quantity";
    document.getElementById(elementId).value = val; 
}

function deleteElement(elementId){
    // Removes an element from the document
    var element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}

function end_order(elementId){
    deleteElement(elementId);
    
    session.service("ALMemory").then(function (memory) {
	memory.raiseEvent("end_order", 1);
    });
}

function showOrder(){
    // create page elements
    var mainDiv = document.getElementById("order");
    var num;
    for(num = 0; num < user_cmd.length; ++num){  // iterate through order items
	var orderItemDiv = document.createElement("div");
	orderItemDiv.className = "orderItem";
	orderItemDiv.id = "orderItem" + num;
	var qteName = document.createElement("p");
	itemName.textContent = user_cmd[num].qte; // insert here item qte
	itemName.className = "qteCol";
	var itemName = document.createElement("p");
	itemName.textContent = user_cmd[num].name; // insert here item name
	itemName.className = "nameCol";
	var itemPrice = document.createElement("p");
	itemPrice.textContent = user_cmd[num].price + "€"; // insert here item price
	itemPrice.className = "priceCol";
	var itemDelete = document.createElement("button");
	itemDelete.type = "button";
	itemDelete.value = "item" + num;
	itemDelete.textContent = "Supprimer";
	itemDelete.onclick = deleteElement(orderItemDiv.id);
	orderItemDiv.appendChild(itemName);
	orderItemDiv.appendChild(itemPrice);
	orderItemDiv.appendChild(itemDelete);
	mainDiv.appendChild(orderItemDiv);
    }
    
    var separator = document.createElement("div");
    separator.appendChild(document.createElement("hr"));
    separator.className = "orderItem";  // to clear floats
    mainDiv.appendChild(separator);

    // print total
    var totalDiv = document.createElement("div");
    totalDiv.className = "orderItem";
    var itemName = document.createElement("p");
    itemName.textContent = "total";
    itemName.className = "nameCol";
    var itemPrice = document.createElement("p");
    itemPrice.textContent = cost() + "€";
    itemPrice.className = "priceCol";
    totalDiv.appendChild(itemName);
    totalDiv.appendChild(itemPrice);
    mainDiv.appendChild(totalDiv);
}

