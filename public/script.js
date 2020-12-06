const buttons = document.getElementById("buttons");

buttons.addEventListener("click", showImage);

function showImage() {
  const elemento = document.getElementById("buttons")

  elemento.addEventListener("click", function (event) {
    const clicado = event.target.className;

    const image = document.createElement("img");
    image.src = `./imagens/${clicado}.png`;
    image.id = "photo";
    image.alt = "demonstração";

    const divImg = document.getElementById("image");

    document.getElementById("photo").remove();
    document.getElementById("text").innerHTML=`Passo ${clicado}`
    divImg.appendChild(image)
  })}
