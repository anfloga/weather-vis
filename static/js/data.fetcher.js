class Point {
    constructor(x, y, dat) {
        this.x = x;
        this.y = y;
        this.dat = dat;
    }

    getPointMesh() {
        var meshGeometry = new THREE.BoxGeometry(2, this.dat, 2);
        meshGeometry.translate(this.x, this.dat / 2, this.y);

        return new THREE.Mesh(meshGeometry);
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

function init() {
    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 10 );
    camera.position.z = 1;

    scene = new THREE.Scene();

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
}

function buildLayer(url) {
    var layer = new Layer();
    var pointArray = fetchAsync(url);

    for (var pointData in pointArray) {
        var point = new Point(pointData.x, pointData.y, pointData.Cloud_Top_Height);
        layer.addToMesh(point);
    }

    layer.addToScene(scene);
}

async function fetchAsync (url) {
    let data = await (await fetch(url)).json();
    return data;
}

var camera, scene, renderer;
init();
buildLayer("http://127.0.0.1:5000/get");

