import { Component } from '@angular/core';

@Component({
    selector: 'app-manage-modules',
    standalone: true,
    imports: [],
    templateUrl: './manage-modules.component.html'
})
export class ManageModulesComponent {
    modules = [
        { id: 1, name: 'Module One', description: 'Example module details' },
        { id: 2, name: 'Module Two', description: 'Another module example' }
    ];

    isAddModalOpen = false;

    openAddModal() {
        this.isAddModalOpen = true;
    }

    closeAddModal() {
        this.isAddModalOpen = false;
    }
}
