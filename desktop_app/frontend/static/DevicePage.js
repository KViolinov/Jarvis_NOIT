class DeviceManager {
    constructor() {
        this.devices = this.loadDevices();
        this.deviceList = document.getElementById('deviceList');
        this.deviceForm = document.getElementById('deviceForm');
 
        this.initEventListeners();
        this.renderDevices();
    }
 
    initEventListeners() {
        this.deviceForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addDevice();
        });
    }
 
    addDevice() {
        const name = document.getElementById('deviceName').value;
        const type = document.getElementById('deviceType').value;
        const status = document.getElementById('deviceStatus').checked ? 'Online' : 'Offline';
 
        const device = {
            id: this.generateDeviceId(),
            name,
            type,
            status
        };
 
        this.devices.push(device);
        this.saveDevices();
        this.renderDevices();
        this.resetForm();
        this.showToast('Device added successfully!', 'success');
    }
 
    renderDevices() {
        this.deviceList.innerHTML = '';
 
        this.devices.forEach(device => {
            const col = document.createElement('div');
            col.className = 'col-md-4';
 
            col.innerHTML = `
                <div class="card device-card shadow-sm">
                    <div class="card-body text-center">
                        <div class="device-icon mb-3">
                            ${this.getDeviceIcon(device.type)}
                        </div>
                        <h5 class="card-title">${device.name}</h5>
                        <p class="card-text">
                            <span class="badge ${device.status === 'Online' ? 'bg-success' : 'bg-secondary'}">
                                ${device.status}
                            </span>
                        </p>
                        <button class="btn btn-sm btn-outline-primary me-2" onclick="deviceManager.toggleStatus('${device.id}')">
                            Toggle Status
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deviceManager.deleteDevice('${device.id}')">
                            Delete
                        </button>
                    </div>
                </div>
            `;
 
            this.deviceList.appendChild(col);
        });
    }
 
    toggleStatus(id) {
        const device = this.devices.find(d => d.id === id);
        if (device) {
            device.status = device.status === 'Online' ? 'Offline' : 'Online';
            this.saveDevices();
            this.renderDevices();
        }
    }
 
    deleteDevice(id) {
        this.devices = this.devices.filter(d => d.id !== id);
        this.saveDevices();
        this.renderDevices();
        this.showToast('Device deleted successfully!', 'danger');
    }
 
    getDeviceIcon(type) {
        const icons = {
            laptop: `<i class="bi bi-laptop fs-1 text-info"></i>`,
            tv: `<i class="bi bi-tv fs-1 text-success"></i>`,
            camera: `<i class="bi bi-camera-video fs-1 text-warning"></i>`,
            light: `<i class="bi bi-lightbulb fs-1 text-warning"></i>`,
            phone: `<i class="bi bi-phone fs-1 text-primary"></i>`,
            router: `<i class="bi bi-hdd-network fs-1 text-danger"></i>`,
            default: `<i class="bi bi-cpu fs-1 text-secondary"></i>`
        };
 
        return icons[type] || icons.default;
    }
 
    saveDevices() {
        localStorage.setItem('devices', JSON.stringify(this.devices));
    }
 
    loadDevices() {
        return JSON.parse(localStorage.getItem('devices')) || [];
    }
 
    resetForm() {
        this.deviceForm.reset();
    }
 
    generateDeviceId() {
        return 'dev-' + Math.random().toString(36).substr(2, 9);
    }
 
    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast-message ${type}`;
        toast.textContent = message;
 
        document.body.appendChild(toast);
 
        setTimeout(() => {
            toast.classList.add('show');
        }, 50);
 
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}
 
// Инициализация на DeviceManager
const deviceManager = new DeviceManager();