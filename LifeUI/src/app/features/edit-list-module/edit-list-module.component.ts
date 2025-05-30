import { Component, ElementRef, inject, ViewChild } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ListService } from '@core/services/list.service';
import { SpinningIconComponent } from '@shared/icons/spinning-icon/spinning-icon.component';
import { ListConfiguration, ListConfigurationDetails, ListField, ListFieldOption } from '@core/models/list.model';
import { ModalComponent } from '@layout/modal/modal.component';
import { FormsModule } from '@angular/forms';
import { ModuleService } from '@core/services/module.service';
import { FieldType } from '@core/models/fieldType.model';
import { ReferenceService } from '@core/services/reference.service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionAdd,
    ionTrashBin,
    ionPencil
} from '@ng-icons/ionicons';
import { LoggerService } from '@core/services/logger.service';

@Component({
    standalone: true,
    selector: 'app-edit-list-module',
    imports: [CommonModule, SpinningIconComponent, ModalComponent, FormsModule, NgIcon, RouterLink],
    providers: [provideIcons({
        ionAdd,
        ionTrashBin,
        ionPencil
    })],
    templateUrl: './edit-list-module.component.html'
})
export class EditListModuleComponent {
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    private listService = inject(ListService);
    private moduleService = inject(ModuleService);
    private referenceService = inject(ReferenceService);
    private logger = inject(LoggerService);

    moduleId = Number(this.route.snapshot.paramMap.get('id'));
    moduleData: ListConfiguration | null = null;
    fieldTypes: FieldType[] = [];
    isLoading = true;
    isEditDetailsModalOpen = false;
    editDetailsForm = {
        name: '',
        order: 1,
        is_enabled: false,
        is_read_only: false,
        is_checkable: false
    };
    isSetFieldModalOpen = false;
    setFieldForm: ListField = {
        id: undefined,
        user_module: this.moduleId,
        field_name: '',
        field_type: 0,
        is_mandatory: false,
        order: 1 + (this.moduleData?.list_fields.length ?? 1),
        rules: [],
        options: []
    };

    @ViewChild('fieldNameInput') fieldNameInput!: ElementRef<HTMLInputElement>;
    @ViewChild('moduleNameInput') moduleNameInput!: ElementRef<HTMLInputElement>;

    ngOnInit(): void {
        this.listService.getModule(this.moduleId).subscribe({
            next: (res) => {
                this.moduleData = res;
                this.isLoading = false;
            },
            error: (error) => {
                this.isLoading = false;
                alert('Module not found');
                this.router.navigate(['/modules']);
            }
        });

        this.referenceService.getFieldTypesWithRules().subscribe({
            next: (res) => {
                this.fieldTypes = res;
            },
            error: (error) => {
                this.logger.error('Error fetching field types', error);
            }
        })
    }

    openEditDetailsModal(): void {
        if (!this.moduleData) return;

        const { name, order, is_enabled, is_read_only, is_checkable } = this.moduleData;
        this.editDetailsForm = { name, order, is_enabled, is_read_only, is_checkable };
        this.isEditDetailsModalOpen = true;

        setTimeout(() => {
            this.moduleNameInput.nativeElement.focus();
        }, 0);
    }

    closeEditModal(): void {
        this.isEditDetailsModalOpen = false;
    }

    saveEditedModule(): void {
        const updated: ListConfigurationDetails = {
            ...this.editDetailsForm,
            id: this.moduleId
        };

        this.listService.updateModuleDetails(updated).subscribe({
            next: (res) => {
                this.moduleData = res;
            },
            error: (error) => {
                this.logger.error('Error updating module details', error);
            }
        });

        this.closeEditModal();
    }

    confirmDeleteModule(): void {
        const confirmed = confirm('Are you sure you want to delete this list? All data will be removed and cannot be restored.');
        if (confirmed) {
            this.deleteModule();
        }
    }

    deleteModule(): void {
        this.moduleService.deleteModule(this.moduleId).subscribe({
            next: () => {
                this.router.navigate(['/modules']);
            },
            error: (error) => {
                this.logger.error('Error deleting module', error);
            }
        });
    }

    openSetFieldModal(field?: ListField): void {
        if (!this.moduleData) return;

        if (field) {
            this.setFieldForm = structuredClone(field);
        } else {
            this.setFieldForm = {
                id: undefined,
                user_module: this.moduleId,
                field_name: '',
                field_type: 0,
                is_mandatory: false,
                order: 1 + (this.moduleData?.list_fields.length ?? 1),
                rules: [],
                options: []
            };
        }

        this.isSetFieldModalOpen = true;

        setTimeout(() => {
            this.fieldNameInput.nativeElement.focus();
        });
    }

    closeSetFieldModal(): void {
        this.isSetFieldModalOpen = false;
    }

    addOption(): void {
        this.setFieldForm.options.push({
            id: undefined,
            option_name: ''
        });
    }

    hasRules(): boolean {
        const type = this.fieldTypes.find(t => t.id === this.setFieldForm.field_type);
        return !!type && !!type.rules && type.rules.length > 0;
    }

    isRuleSelected(ruleId: number): boolean {
        return this.setFieldForm.rules.some(r => r.id === ruleId);
    }

    toggleRule(rule: any): void {
        const exists = this.setFieldForm.rules.some(r => r.id === rule.id);
        if (exists) {
            this.setFieldForm.rules = this.setFieldForm.rules.filter(r => r.id !== rule.id);
        } else {
            this.setFieldForm.rules.push(rule);
        }
    }

    get selectedRules() {
        return this.fieldTypes.find(t => t.id === this.setFieldForm.field_type)?.rules ?? [];
    }

    get sortedFields() {
        return this.moduleData?.list_fields.sort((a, b) => a.order - b.order) ?? [];
    }

    get optionName() {
        return this.fieldTypes.find(t => t.id === this.setFieldForm.field_type)?.name;
    }

    onFieldTypeChange(value: number): void {
        this.setFieldForm.field_type = +value;
        this.setFieldForm.rules = [];
        this.setFieldForm.options = [];

        if (this.optionName === 'dropdown') {
            this.addOption();
        }
    }

    saveSetField(): void {
        // Validate all options have values
        if (this.fieldTypes.find(t => t.id === this.setFieldForm.field_type)?.name.toLowerCase() === 'dropdown') {
            if (!this.setFieldForm.options.length) {
                alert('Please add at least one option');
                return;
            }

            const hasEmptyOption = this.setFieldForm.options.some(o => !o.option_name);
            if (hasEmptyOption) {
                alert('All options must have a value');
                return;
            }
        }
        else {
            this.setFieldForm.options = [];
        }

        if (this.setFieldForm.id) {
            this.listService.updateField(this.moduleId, this.setFieldForm.id!, this.setFieldForm).subscribe({
                next: (field: ListField) => {
                    this.closeSetFieldModal();
                    this.moduleData!.list_fields = this.moduleData!.list_fields.map(f => f.id === field.id ? field : f);
                },
                error: (error) => {
                    this.logger.error('Error updating field', error);
                }
            });
        }
        else {
            this.listService.addField(this.moduleId, this.setFieldForm).subscribe({
                next: (field: ListField) => {
                    this.closeSetFieldModal();
                    this.moduleData!.list_fields.push(field);
                },
                error: (error) => {
                    this.logger.error('Error adding field', error);
                }
            });
        }
    }

    confirmDeleteField(fieldId: number): void {
        const confirmed = confirm('Are you sure you want to delete this field? All data saved to this field will be removed and cannot be restored.');
        if (confirmed) {
            this.deleteField(fieldId);
        }
    }

    deleteField(fieldId: number): void {
        this.listService.deleteField(this.moduleId, fieldId).subscribe({
            next: () => {
                this.moduleData = {
                    ...this.moduleData!,
                    list_fields: this.moduleData!.list_fields.filter(f => f.id !== fieldId)
                };
            },
            error: (error) => {
                this.logger.error('Error deleting field', error);
            }
        });
    }

    removeOption(option: ListFieldOption, index: number): void {
        if (!option.id) {
            this.setFieldForm.options.splice(index, 1);
            return;
        }
        this.setFieldForm.options = this.setFieldForm.options.filter(o => o.id !== option.id);
    }
}
