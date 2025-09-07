class FlashMessage{
    constructor(message, type) {
        this.message = message;
        this.type = type;
    }

    show() {
        let alert_container = document.getElementById("notifications-container");
        if (this.type == 'success'){
            alert_container.insertAdjacentHTML('beforeend', `
                <div x-data="{ show: true }" x-show="show" x-transition.opacity x-init="setTimeout(() => show = false, 3000)" class="w-full px-4 py-2 bg-green-700 shadow rounded text-white text-sm">
                    <p>${this.message}</p>
                </div>
            `);
        }else if (this.type == 'error'){
            alert_container.insertAdjacentHTML('beforeend', `
                <div x-data="{ show: true }" x-show="show" x-transition.opacity x-init="setTimeout(() => show = false, 3000)" class="w-full px-4 py-2 bg-red-700 shadow rounded text-white text-sm">
                    <p>${this.message}</p>
                </div>
            `);
        }
    }
}