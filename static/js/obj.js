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
        console.log(this.material);
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.scale.set(4, 4, 0.01);
        scene.add(this.mesh);
        console.log("layer added");
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
        this.material = new THREE.MeshPhongMaterial({color: 0xdddddd, wireframe: true});
        this.geometry = new THREE.PlaneGeometry(100, 100, 400, 400);
    }

    setSegmentHeight(point) {
        var x = Math.round(point.x);
        var y = Math.round(point.y);
        var index = x * y;
        this.geometry.vertices[index].z = point.dat;
    }

    async setMaterial() {
        //var texture = new THREE.TextureLoader().load("/static/modis_granule_rgb_color_enh.png");
        var texture = new THREE.TextureLoader().load("/static/modis_granule_rgb_color_enh.png");
        //this.material = new THREE.MeshBasicMaterial( { map: texture } );
        this.material = new THREE.MeshBasicMaterial( { map: texture } );
    }
}


class BufferLayer extends Layer {
    constructor() {
        super();
        this.geometry = new THREE.BufferGeometry();
    }


    async setMaterial() {
        var texture = new THREE.TextureLoader().load("/static/modis_granule_rgb_color_enh.png");
        //this.material = new THREE.MeshBasicMaterial( { map: texture } );
        //this.material = new THREE.MeshNormalMaterial( { map: texture } );

        //this.material = new THREE.MeshPhongMaterial( {
			//color: 0xaaaaaa, specular: 0xffffff, shininess: 250,
			//side: THREE.DoubleSide, vertexColors: THREE.VertexColors
		//} );
        this.material = new THREE.MeshBasicMaterial({
            vertexColors: THREE.VertexColors,
            transparent: true
        });

        console.log("material set");
        console.log(this.material);
    }

    async setTexture() {
        //var texture = new THREE.TextureLoader().load("/static/modis_granule_rgb_color_enh.png");

        //texture.minFilter = THREE.NearestFilter;

        var texture = new THREE.TextureLoader().load("/static/square.png");
        this.material = new THREE.MeshBasicMaterial( { map: texture } );
        //this.material = new THREE.MeshPhongMaterial( { map: texture } );
        //this.material = new THREE.MeshNormalMaterial( { map: texture } );

        //this.material = new THREE.MeshPhongMaterial( {
		//	color: 0xaaaaaa, specular: 0xffffff, shininess: 250,
		//	side: THREE.DoubleSide,
	    //  map: texture
        //} );
        console.log("material set");
        console.log(this.material);
    }

    async setShader() {

        var texture = new THREE.TextureLoader().load("/static/cloud10.png");
            texture.magFilter = THREE.LinearMipMapLinearFilter;
            texture.minFilter = THREE.LinearMipMapLinearFilter;

            var fog = new THREE.Fog( 0x4584b4, - 100, 3000 );

            this.material = new THREE.ShaderMaterial( {

                uniforms: {

                    "map": { type: "t", value: texture },
                    "fogColor" : { type: "c", value: fog.color },
                    "fogNear" : { type: "f", value: fog.near },
                    "fogFar" : { type: "f", value: fog.far },

                },
                vertexShader: document.getElementById( 'vs' ).textContent,
                fragmentShader: document.getElementById( 'fs' ).textContent,
                depthWrite: false,
                depthTest: false,
                transparent: true

            } );
    }

//    async setMaterial() {
        //var textureLoader = new THREE.TextureLoader();
//        var image = await fetch("/static/modis_granule_rgb_color_enh.png");
        //var material = new THREE.MeshBasicMaterial();
        //textureLoader.load( "/static/modis_granule_rgb_color_enh.png", function (texture) { material = new THREE.MeshBasicMaterial({ map: texture }); console.log("material loaded"); console.log(material); }, undefined, function (err) { console.log("error!"); } );
        //console.log(material);
        //this.material = material;
        //this.material = new THREE.MeshBasicMaterial( { map: texture, side: THREE.DoubleSide } );
    //}
}


function getCamera() {
    var camera;
    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.1, 10000);
    //camera.position.set(100, 100, 400);
    //camera.lookAt(new THREE.Vector3(100, 100, 0));
    camera.position.y = -200;
    camera.position.z = 100;
    var controls = new THREE.OrbitControls(camera);
//    controls.target.set(100, 0, 100);
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
        var point = new Point(pointData.x, pointData.y, pointData.z);
        layer.addPoint(point);
    }

    layer.addToScene(scene);
}


async function buildPlaneLayer(url) {
    var layer = new PlaneLayer(2, 2);
    var raw = await fetch(url);
    var pointArray = await raw.json();

    for (var key in pointArray) {
        var pointData = pointArray[key];
        var point = new Point(pointData.x, pointData.y, pointData.z);
        layer.setSegmentHeight(point);
    }

    await layer.setMaterial();
    layer.addToScene(scene);
}


async function buildTestLayer() {
    var layer = new PlaneLayer(2, 2);

    await layer.setMaterial();
    layer.addToScene(scene);
}


async function buildBufferLayer(url, zheight) {
    var layer = new BufferLayer();
    await layer.setMaterial();
    var positions = [];
	var normals = [];
    var colours = [];
    var uvs = [];
    var alphas = [];
    var colour = new THREE.Color();

    var pA = new THREE.Vector3();
    var pB = new THREE.Vector3();
    var pC = new THREE.Vector3();

    var cb = new THREE.Vector3();
    var ab = new THREE.Vector3();

    var raw = await fetch(url);
    var vertexArray = await raw.json();

    for (var key in vertexArray) {
        var vertex = vertexArray[key];

        positions.push(vertex.ax, vertex.ay, vertex.az + zheight);
        positions.push(vertex.bx, vertex.by, vertex.bz + zheight);
        positions.push(vertex.cx, vertex.cy, vertex.cz + zheight);

        pA.set(vertex.ax, vertex.ay, vertex.az);
        pB.set(vertex.bx, vertex.by, vertex.bz);
        pC.set(vertex.cx, vertex.cy, vertex.cz);

        cb.subVectors( pC, pB );
        ab.subVectors( pA, pB );
        cb.cross( ab );

        cb.normalize();

        var nx = cb.x;
        var ny = cb.y;
        var nz = cb.z;

        normals.push( nx, ny, nz );
        normals.push( nx, ny, nz );
        normals.push( nx, ny, nz );

        var vx = ( Math.max(vertex.ax, vertex.bx, vertex.cx) / 500 );
        var vy = ( Math.max(vertex.ay, vertex.by, vertex.cy) / 500 );
        var vz = ( Math.max(vertex.az, vertex.bz, vertex.cz) / 170 );


        //red-to-blue heatmap logic
        //var redColour = (vertex.az + vertex.bz + vertex.cz) / 3.0;
        //redColour = redColour / 17000.0;
        //var greenColour = 1 - redColour

        var redColour = ((vertex.az + vertex.bz + vertex.cz) / 3.0) / 65535.0;
        var blueColour = ((vertex.az + vertex.bz + vertex.cz) / 3.0) / 65535.0;
        var greenColour = ((vertex.az + vertex.bz + vertex.cz) / 3.0) / 65535.0;

        colour.setRGB( redColour, blueColour, greenColour );

        var uvArray = new Float32Array([
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0,
            0.0, 1.0,
        ])

        for (var i = 0, len = 9; i < len; i++) {
            uvs.push(uvArray);
        }

        var alpha = ((vertex.az + vertex.bz + vertex.cz) / 3.0);
        alphas.push(alpha);

        //colour.setRGB( Math.random(), Math.random(), Math.random());
        colours.push( colour.r, colour.g, colour.b );
        colours.push( colour.r, colour.g, colour.b );
        colours.push( colour.r, colour.g, colour.b );
    }

    layer.geometry.addAttribute( 'position', new THREE.Float32BufferAttribute( positions, 3 ).onUpload( disposeArray ) );
    layer.geometry.addAttribute( 'normal', new THREE.Float32BufferAttribute( normals, 3 ).onUpload( disposeArray ) );
    layer.geometry.addAttribute( 'color', new THREE.Float32BufferAttribute( colours, 3 ).onUpload( disposeArray ) );
    //layer.geometry.addAttribute( 'uv', new THREE.Float32BufferAttribute( uvs, 0 ).onUpload( disposeArray ) );
    layer.geometry.addAttribute( 'alpha', new THREE.Float32BufferAttribute( alphas, 1 ).onUpload( disposeArray ) );
    layer.geometry.computeBoundingSphere();

    //console.log(layer.geometry);
    //console.log(layer.material);

    layer.addToScene(scene);
}


function disposeArray() {
    this.array = null;
}


function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

var scene = new THREE.Scene();

scene.background = new THREE.Color(0xffffff);
//scene.background = new THREE.Color(0xffffff);
var light = new THREE.DirectionalLight( 0xffffff );
light.position.set( 0, 1, 1 ).normalize();
scene.add(light);

scene.add( new THREE.AmbientLight( 0x444444 ) );

var light1 = new THREE.DirectionalLight( 0xffffff, 0.5 );
light1.position.set( 1, 1, 1 );
scene.add( light1 );

var light2 = new THREE.DirectionalLight( 0xffffff, 1.5 );
light2.position.set( 0, -1, 0 );
scene.add( light2 );



var camera = getCamera();
var renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

buildBufferLayer("http://127.0.0.1:5000/layer?name=base", -100000);
buildBufferLayer("http://127.0.0.1:5000/layer?name=top", 100000);
//buildTestLayer();
animate();
