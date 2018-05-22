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
        this.mesh = new THREE.Mesh(this.geometry, new THREE.MeshBasicMaterial({color: 0xffff00}));
        scene.add(this.mesh);
    }
}

function getCamera() {
    var camera;
    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 10000 );
    camera.position.z = 400;

    var controls = new THREE.OrbitControls(camera);
    return camera;
}

function render(scene, camera) {
    var renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
    renderer.render(scene, camera);
}

async function buildLayer(url) {
    var layer = new Layer();
    var raw = await fetch(url);
    var pointArray = await raw.json();

    for (var key in pointArray) {
        var pointData = pointArray[key];
        var point = new Point(pointData.x, pointData.y, pointData.Cloud_Top_Height);
        layer.addToMesh(point);
    }
    layer.addToScene(scene);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

var scene = new THREE.Scene();
var camera = getCamera();
var renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

buildLayer("http://127.0.0.1:5000/get");
animate();
