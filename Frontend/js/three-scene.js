/**
 * 3D Animated Background using Three.js
 * Particle system with dynamic connections, floating geometry, and glow effects
 */

class ThreeScene {
    constructor() {
        this.canvas = document.getElementById('bg-canvas');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.geometries = [];
        this.mouse = { x: 0, y: 0 };
        this.clock = new THREE.Clock();
        this.lines = [];

        this.init();
        this.createParticles();
        this.createFloatingGeometry();
        this.createGlowOrbs();
        this.addEventListeners();
        this.animate();
    }

    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x0a0a1a, 0.0008);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60, window.innerWidth / window.innerHeight, 1, 2000
        );
        this.camera.position.z = 500;
        this.camera.position.y = 100;

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setClearColor(0x0a0a1a, 1);
    }

    createParticles() {
        const particleCount = 1500;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);

        const colorPalette = [
            new THREE.Color(0x00f5ff),  // Cyan
            new THREE.Color(0x7c3aed),  // Purple
            new THREE.Color(0x3b82f6),  // Blue
            new THREE.Color(0xf472b6),  // Pink
        ];

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 2000;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 1200;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 1500;

            const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;

            sizes[i] = Math.random() * 3 + 1;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

        const material = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending,
            sizeAttenuation: true
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    createFloatingGeometry() {
        const geometryTypes = [
            () => new THREE.IcosahedronGeometry(15, 1),
            () => new THREE.OctahedronGeometry(12, 0),
            () => new THREE.TetrahedronGeometry(10, 0),
            () => new THREE.TorusGeometry(10, 3, 8, 16),
            () => new THREE.DodecahedronGeometry(12, 0),
        ];

        for (let i = 0; i < 12; i++) {
            const geoFn = geometryTypes[Math.floor(Math.random() * geometryTypes.length)];
            const geometry = geoFn();

            const hue = Math.random();
            const color = new THREE.Color().setHSL(hue, 0.8, 0.5);

            const material = new THREE.MeshBasicMaterial({
                color: color,
                wireframe: true,
                transparent: true,
                opacity: 0.12,
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                (Math.random() - 0.5) * 1500,
                (Math.random() - 0.5) * 800,
                (Math.random() - 0.5) * 1000
            );

            mesh.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.01,
                    y: (Math.random() - 0.5) * 0.01,
                    z: (Math.random() - 0.5) * 0.01
                },
                floatSpeed: Math.random() * 0.5 + 0.2,
                floatAmplitude: Math.random() * 30 + 10,
                initialY: mesh.position.y,
                phase: Math.random() * Math.PI * 2
            };

            this.geometries.push(mesh);
            this.scene.add(mesh);
        }
    }

    createGlowOrbs() {
        const orbPositions = [
            { x: -400, y: 200, z: -300, color: 0x00f5ff, size: 40 },
            { x: 350, y: -150, z: -400, color: 0x7c3aed, size: 35 },
            { x: -200, y: -200, z: -200, color: 0xf472b6, size: 30 },
            { x: 500, y: 100, z: -500, color: 0x3b82f6, size: 45 },
        ];

        orbPositions.forEach(orbData => {
            const geometry = new THREE.SphereGeometry(orbData.size, 32, 32);
            const material = new THREE.MeshBasicMaterial({
                color: orbData.color,
                transparent: true,
                opacity: 0.04,
            });

            const orb = new THREE.Mesh(geometry, material);
            orb.position.set(orbData.x, orbData.y, orbData.z);
            orb.userData = {
                initialPos: { ...orbData },
                phase: Math.random() * Math.PI * 2
            };

            this.geometries.push(orb);
            this.scene.add(orb);
        });
    }

    addEventListeners() {
        window.addEventListener('resize', () => this.onResize());
        window.addEventListener('mousemove', (e) => this.onMouseMove(e));
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    onMouseMove(event) {
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const time = this.clock.getElapsedTime();

        // Rotate particles
        if (this.particles) {
            this.particles.rotation.y += 0.0003;
            this.particles.rotation.x += 0.0001;

            // Subtle mouse interaction
            this.particles.rotation.y += this.mouse.x * 0.0002;
            this.particles.rotation.x += this.mouse.y * 0.0001;
        }

        // Animate floating geometries
        this.geometries.forEach(mesh => {
            if (mesh.userData.rotationSpeed) {
                mesh.rotation.x += mesh.userData.rotationSpeed.x;
                mesh.rotation.y += mesh.userData.rotationSpeed.y;
                mesh.rotation.z += mesh.userData.rotationSpeed.z;

                mesh.position.y = mesh.userData.initialY +
                    Math.sin(time * mesh.userData.floatSpeed + mesh.userData.phase) *
                    mesh.userData.floatAmplitude;
            }

            if (mesh.userData.initialPos) {
                mesh.position.y = mesh.userData.initialPos.y +
                    Math.sin(time * 0.3 + mesh.userData.phase) * 20;

                const scale = 1 + Math.sin(time * 0.5 + mesh.userData.phase) * 0.1;
                mesh.scale.setScalar(scale);
            }
        });

        // Camera subtle movement
        this.camera.position.x += (this.mouse.x * 30 - this.camera.position.x) * 0.02;
        this.camera.position.y += (this.mouse.y * 20 + 100 - this.camera.position.y) * 0.02;
        this.camera.lookAt(this.scene.position);

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize 3D Scene
const threeScene = new ThreeScene();