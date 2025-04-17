import { Component, OnInit } from '@angular/core';
import { ModuleService } from '../../core/services/module.service';
import { ModuleType } from '../../core/models/moduleType.model';
import { UserModule } from '../../core/models/userModule.model';

@Component({
    selector: 'app-manage-modules',
    standalone: true,
    imports: [],
    templateUrl: './manage-modules.component.html'
})
export class ManageModulesComponent implements OnInit {
    modules: UserModule[] = [];
    isAddModalOpen = false;
    moduleTypes: ModuleType[] = [];

    constructor(private moduleService: ModuleService) { }

    ngOnInit(): void {
        // Load module types
        this.moduleService.getModuleTypes().subscribe({
            next: (res) => this.moduleTypes = res,
            error: (err) => console.error('Failed to load module types', err)
        })

        // Load users modules
        this.moduleService.getUserModules().subscribe({
            next: (res) => this.modules = res.results,
            error: (err) => console.error('Failed to load modules', err)
        });
    }

    openAddModal() {
        this.isAddModalOpen = true;
    }

    closeAddModal() {
        this.isAddModalOpen = false;
    }
}
