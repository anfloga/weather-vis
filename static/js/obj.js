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
        this.material = new THREE.MeshBasicMaterial({color: 0xffff00});
        this.geometry = new THREE.Geometry();
        this.mesh = new THREE.Mesh();
    }

    addToScene(scene) {
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        scene.add(this.mesh);
    }
}

class PointLayer extends Layer {
    constructor() {
        super();
    }

    addPoint(point) {
        this.geometry.mergeMesh(point.getPointMesh());
    }
}


class PlaneLayer extends Layer {
    constructor(x, y) {
        super();
        //this.material = new THREE.MeshPhongMaterial({color: 0xdddddd, wireframe: false});
        this.geometry = new THREE.PlaneGeometry(x * 400, y * 400, 800, 800);
    }

    setSegmentHeight(point) {
        var x = Math.round(point.x);
        var y = Math.round(point.y);
        var index = x * y;
        this.geometry.vertices[index].z = point.dat;
    }
}




function getCamera() {
    var camera;
    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 10000 );
    //camera.position.set(100, 100, 400);
    //camera.lookAt(new THREE.Vector3(100, 100, 0));

    var controls = new THREE.OrbitControls(camera);
    controls.target.set(100, 0, 100);
    return camera;
}

function render(scene, camera) {
    var renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );
    renderer.render(scene, camera);
}

async function buildPointLayer(url) {
    var layer = new PointLayer();
    var raw = await fetch(url);
    var pointArray = await raw.json();

    for (var key in pointArray) {
        var pointData = pointArray[key];
        var point = new Point(pointData.x, pointData.y, pointData.Cloud_Top_Height);
        layer.addPoint(point);
    }
    layer.addToScene(scene);
}

async function buildPlaneLayer(url) {
    var layer = new PlaneLayer();
    var raw = await fetch(url);
    var pointArray = await raw.json();

    for (var key in pointArray) {
        var pointData = pointArray[key];
        var point = new Point(pointData.x, pointData.y, pointData.Cloud_Top_Height);
        layer.setSegmentHeight(point);
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

buildPlaneLayer("http://127.0.0.1:5000/get");
animate();
