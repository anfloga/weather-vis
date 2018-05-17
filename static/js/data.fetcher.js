class Point {
    constructor(x, y, dat) {
        this.x = x;
        this.y = y;
        this.dat = dat;
    }

    getPointMesh() {
        var meshGeometry = new THREE.BoxGeometry(2, this.dat, 2);
        meshGeometry.translate(this.x, this.dat / 2, this.y);

        var meshMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });

        return new THREE.Mesh(meshGeometry, meshMaterial);
    }
}

class Layer {
    constructor() {
        this.geometry = new THREE.Geometry();
        this.mesh = new THREE.Mesh();
    }

    addToMesh(point) {
        this.geometry.mergeMesh(point.getPointMesh());
    }

    addToScene(scene) {
        this.mesh = new THREE.Mesh(this.geometry);
        scene.add(this.mesh);
        alert("layer added");
    }
}

function getCamera() {
    var camera;
    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 10 );
    camera.position.z = 200;

    return camera;
}

function render(scene, camera) {
    var renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
    renderer.render(scene, camera);
}

function addCube() {
				var texture = new THREE.TextureLoader().load( 'static/textures/crate.gif' );
				var geometry = new THREE.BoxBufferGeometry( 200, 200, 200 );
				var material = new THREE.MeshBasicMaterial( { map: texture } );
				mesh = new THREE.Mesh( geometry, material );
				scene.add( mesh );
}

async function buildLayer(url) {
    var layer = new Layer();
    var raw = await fetch(url);
    var pointArray = await raw.json();

    for (var pointData in pointArray) {
        var point = new Point(pointData.x, pointData.y, pointData.Cloud_Top_Height);
        layer.addToMesh(point);
    }
    console.log(scene);
    layer.addToScene(scene);
}


var scene = new THREE.Scene();
var camera = getCamera();
console.log(scene);
console.log(camera);
addCube();
buildLayer("http://127.0.0.1:5000/get");
render(scene, camera);
