var name = '';
var encoded = null;
var fileExt = null;
var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const synth = window.speechSynthesis;
const recognition = new SpeechRecognition();
const icon = document.querySelector('i.fa.fa-microphone');


///// SEARCH TRIGGER //////
function searchFromVoice() {
  recognition.start();
  recognition.onresult = (event) => {
    const speechToText = event.results[0][0].transcript;
    console.log(speechToText);
    document.getElementById("searchbar").value = speechToText;
    search();
  }
}

function search() {
  var searchTerm = document.getElementById("searchbar").value;
  var apigClient = apigClientFactory.newClient({ apiKey: " " });


    var body = { };
    var params = {q : searchTerm};
    var additionalParams = {headers: {
    'Content-Type':"application/json"
    }};

    apigClient.searchGet(params, body , additionalParams).then(function(res){
        console.log("success");
        console.log(res);
        showImages(res.data)
      }).catch(function(result){
          console.log(result);
          console.log("NO RESULT");
      });

}


/////// SHOW IMAGES BY SEARCH //////

function showImages(res) {
  var newDiv = document.getElementById("images");
  if(typeof(newDiv) != 'undefined' && newDiv != null){
  while (newDiv.firstChild) {
    newDiv.removeChild(newDiv.firstChild);
  }
  }
  console.log("THIS IS RES")
  console.log(res);
  console.log("THIS IS RES.BODY")
  console.log(res.body)
  if (res.length == 0) {
    var newContent = document.createTextNode("No image to display");
    newDiv.appendChild(newContent);
  }
  else {
    results=res
    for (var i = 0; i < results.length; i++) {
      console.log(results[i]);
      var newDiv = document.getElementById("images");
      //newDiv.style.display = 'inline'
      var newimg = document.createElement("img");
      var classname = randomChoice(['big', 'vertical', 'horizontal', '']);
      if(classname){newimg.classList.add();}
      
      filename = results[i].substring(results[i].lastIndexOf('/')+1)
      newimg.src = "https://b2photoss.s3.amazonaws.com/"+filename;
      newDiv.appendChild(newimg);
    }
  }
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}



///// UPLOAD IMAGES ///////

const realFileBtn = document.getElementById("realfile");

function uploadImage() {
  realFileBtn.click(); 
}

function previewFile(input) {
  const clabel = document.getElementById("labels").value;
  var reader = new FileReader();
  name = input.files[0].name;
  console.log(name)
  fileExt = name.split(".").pop();
  
  console.log(fileExt)
  console.log("THIS IS THE EXTENSION!!")

  var onlyname = name.replace(/\.[^/.]+$/, "");
  var finalName = onlyname+"."+fileExt;
  name = finalName;
  console.log("Final name", name)

  reader.onload = function (e) {
    var src = e.target.result;    
    var newImage = document.createElement("img");
    newImage.src = src;
    console.log("New Image", newImage)
    console.log("Source path", src)
    encoded = newImage.outerHTML;
    console.log("Encoded", encoded)

    last_index_quote = encoded.lastIndexOf('"');
    if (fileExt == 'jpg' || fileExt == 'jpeg' || fileExt == 'png') {
      encodedStr = encoded.substring(33, last_index_quote);
    }
    else {
      encodedStr = encoded.substring(32, last_index_quote);
    }

    console.log("Final encoded", encodedStr)
    var apigClient = apigClientFactory.newClient({ apiKey: " " });

    var params = {
        "key": name,
        "bucket": "b2photoss",
        "Content-Type": "image/jpg",
    };

    if(clabel.length > 0){
      var additionalParams = {
        headers: {
          "Content-Type": "image/jpg",
          'x-amz-meta-customlabels': clabel,
        }
      };
    }
    else{
      var additionalParams = {
        headers: {
          "Content-Type": "image/jpg",
        }
      };
    }

    apigClient.uploadBucketKeyPut(params, encodedStr, additionalParams)
      .then(function (result) {
        console.log(result);
        console.log('success OK');
        alert("Photo Uploaded Successfully");
      }).catch(function (result) {
        console.log(result);
      });
    }
   reader.readAsDataURL(input.files[0]);

   
}
