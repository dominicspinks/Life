import { Component, inject, OnInit } from '@angular/core';
import { ModuleService } from '../../core/services/module.service';
import { ModuleType } from '../../core/models/moduleType.model';
import { CreateUserModule, UserModule } from '../../core/models/userModule.model';
import { ModalComponent } from "../../layout/modal/modal.component";
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionEye,
    ionPencil,
} from '@ng-icons/ionicons';

@Component({
    selector: 'app-manage-modules',
    standalone: true,
    imports: [ModalComponent, FormsModule, NgIcon, RouterLink],
    templateUrl: './manage-modules.component.html',
    providers: [provideIcons({ ionEye, ionPencil })]
})
export class ManageModulesComponent implements OnInit {
    private moduleService = inject(ModuleService);
    private router = inject(Router);

    modules: UserModule[] = [];
    moduleTypes: ModuleType[] = [];
    isAddModalOpen = false;

    // Add module modal fields
    selectedType: number = 0;
    newModuleName = '';
    isCheckable = false;
    listTypeId: number | null = null;

    getDefaultModuleTypeId(types: ModuleType[]): number {
        // Default type is 'list'
        if (types.length) {
            const listType = types.find(t => t.name === 'list');
            return listType?.id ?? types[0].id;
        }

        return 0;
    }

    ngOnInit(): void {
        // Load module types
        this.moduleService.getModuleTypes().subscribe({
            next: (res) => {
                this.moduleTypes = res;

                const listType = this.moduleTypes.find(t => t.name === 'list');
                this.listTypeId = listType?.id ?? null;

                this.selectedType = this.getDefaultModuleTypeId(this.moduleTypes);
            },
            error: (err) => console.error('Failed to load module types', err)
        });

        // Load users modules
        this.moduleService.getUserModules(true).subscribe({
            next: (res) => this.modules = res.results,
            error: (err) => console.error('Failed to load modules', err)
        });
    }

    openAddModal() {
        this.selectedType = this.getDefaultModuleTypeId(this.moduleTypes);
        this.newModuleName = '';
        this.isCheckable = false;
        this.isAddModalOpen = true;
    }

    closeAddModal() {
        this.isAddModalOpen = false;
    }

    saveModule(): void {
        if (!this.newModuleName.trim()) {
            alert('Module name is required');
            return;
        }

        const newModule: CreateUserModule = {
            module: this.selectedType,
            name: this.newModuleName.trim(),
            order: this.modules.length + 1,
            is_enabled: true,
            is_read_only: false,
            is_checkable: this.selectedType === this.listTypeId ? this.isCheckable : false
        };

        this.moduleService.addModule(newModule).subscribe({
            next: (createdModule) => {
                this.modules.push(createdModule);
                this.closeAddModal();

                // Navigate to the edit page if it's a list module
                if (this.selectedType === this.listTypeId) {
                    this.router.navigate([`/modules/list/${createdModule.id}/edit`]);
                }
            },
            error: (err) => {
                console.error('Failed to add module:', err);
                alert('Failed to save module. Please try again.');
            }
        });
    }

    openViewPage(moduleId: number) {
        this.router.navigate([`/modules/list/${moduleId}`]);
    }

    openEditPage(moduleId: number) {
        this.router.navigate([`/modules/list/${moduleId}/edit`]);
    }
}
