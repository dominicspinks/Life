import { Component, inject } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
    ionAdd,
    ionTrashBin,
    ionPencil,
    ionMenu
} from '@ng-icons/ionicons';
import { LoggerService } from '../../../../core/services/logger.service';
import { BudgetService } from '../../../../core/services/budget.service';
import { SpinningIconComponent } from '../../../../shared/icons/spinning-icon/spinning-icon.component';
import { ModalComponent } from '../../../../layout/modal/modal.component';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { BudgetCategory, BudgetConfiguration, BudgetConfigurationDetails } from '../../../../core/models/budget.model';
import { ModuleService } from '../../../../core/services/module.service';
import { ToastService } from '../../../../shared/ui/toast/toast.service';

@Component({
    selector: 'app-budget-settings-tab',
    standalone: true,
    imports: [NgIcon, SpinningIconComponent, ModalComponent, FormsModule,],
    providers: [provideIcons({
        ionAdd,
        ionTrashBin,
        ionPencil,
        ionMenu
    })],
    templateUrl: './budget-settings-tab.component.html',
    styleUrl: './budget-settings-tab.component.css'
})
export class BudgetSettingsTabComponent {
    private route = inject(ActivatedRoute);
    private router = inject(Router);
    private budgetService = inject(BudgetService);
    private moduleService = inject(ModuleService);
    private logger = inject(LoggerService);
    private toastService = inject(ToastService);

    budgetId = Number(this.route.parent?.snapshot.paramMap.get('id'));
    budgetConfiguration: BudgetConfiguration | null = null;
    sortedCategories: BudgetCategory[] | null = null;
    isLoading = true;
    isEditDetailsModalOpen = false;
    editDetailsForm = {
        name: '',
        order: 1,
        is_enabled: false,
        is_read_only: false,
    };

    isSetCategoryModalOpen = false;
    setCategoryForm: BudgetCategory = {
        id: undefined,
        name: '',
        weekly_target: 0,
        excluded_from_budget: false,
        order: 1,
        is_enabled: true
    };

    draggedCategory: BudgetCategory | null = null;
    dragStartIndex = -1;
    dragTargetIndex = -1;

    ngOnInit(): void {
        // Get budget details from API
        this.budgetService.getBudgetConfiguration(this.budgetId).subscribe({
            next: (res) => {
                this.budgetConfiguration = res;
                this.sortedCategories = [...this.budgetConfiguration.categories];
                this.sortedCategories.sort((a, b) => a.order - b.order);

                this.editDetailsForm = {
                    name: this.budgetConfiguration.name,
                    order: this.budgetConfiguration.order,
                    is_enabled: this.budgetConfiguration.is_enabled,
                    is_read_only: this.budgetConfiguration.is_read_only
                };

                this.setCategoryForm.order = 1 + this.budgetConfiguration.categories.length;
                this.isLoading = false;
            },
            error: (error) => {
                this.isLoading = false;
                this.logger.error('Error fetching budget details', error);
                this.toastService.show('Error fetching budget details', 'error', 3000);
                this.router.navigate(['/modules']);
            }
        })

    }


    openEditDetailsModal(): void {
        if (!this.budgetConfiguration) return;

        const { name, order, is_enabled, is_read_only, is_checkable } = this.budgetConfiguration;
        this.editDetailsForm = { name, order, is_enabled, is_read_only };
        this.isEditDetailsModalOpen = true;
    }

    closeEditModal(): void {
        this.isEditDetailsModalOpen = false;
    }

    saveEditedModule(): void {
        const updated: BudgetConfigurationDetails = {
            ...this.editDetailsForm,
            id: this.budgetConfiguration!.id
        };

        this.budgetService.updateBudgetDetails(updated).subscribe({
            next: (res) => {
                this.budgetConfiguration = res;
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
        this.moduleService.deleteModule(this.budgetConfiguration!.id).subscribe({
            next: () => {
                this.router.navigate(['/modules']);
            },
            error: (error) => {
                this.logger.error('Error deleting module', error);
            }
        });
    }

    openSetCategoryModal(category?: BudgetCategory): void {
        if (!this.budgetConfiguration) return;

        if (category) {
            this.setCategoryForm = structuredClone(category);
        } else {
            this.setCategoryForm = {
                id: undefined,
                name: '',
                weekly_target: 0,
                excluded_from_budget: false,
                order: 1 + (this.budgetConfiguration?.categories.length ?? 1),
                is_enabled: true,
            };
        }

        this.isSetCategoryModalOpen = true;
    }

    closeSetCategoryModal(): void {
        this.isSetCategoryModalOpen = false;
    }

    saveSetCategory(): void {
        // Validate the form
        // Validate name is filled
        if (!this.setCategoryForm.name || this.setCategoryForm.name.trim() === '') {
            this.toastService.show('Name is required', 'error', 3000);
            return;
        }

        // Validate the name is unique
        if (this.budgetConfiguration!.categories.some(c => c.name.toLowerCase() === this.setCategoryForm.name.toLowerCase() && c.id !== this.setCategoryForm.id)) {
            this.toastService.show('Name must be unique', 'error', 3000);
            return;
        }

        // Validate weekly target is filled
        if (!this.setCategoryForm.weekly_target && this.setCategoryForm.weekly_target !== 0) {
            this.toastService.show('Weekly target is required', 'error', 3000);
            return;
        }


        if (this.setCategoryForm.id) {
            this.budgetService.updateCategory(this.budgetConfiguration!.id, this.setCategoryForm.id!, this.setCategoryForm).subscribe({
                next: (category: BudgetCategory) => {
                    this.closeSetCategoryModal();
                    this.budgetConfiguration!.categories = this.budgetConfiguration!.categories.map(c => c.id === category.id ? category : c);
                    this.sortedCategories = this.sortedCategories!.map(c => c.id === category.id ? category : c);
                },
                error: (error) => {
                    this.logger.error('Error updating category', error);
                }
            });
        }
        else {
            this.budgetService.addCategory(this.budgetConfiguration!.id, this.setCategoryForm).subscribe({
                next: (category: BudgetCategory) => {
                    this.closeSetCategoryModal();
                    this.budgetConfiguration!.categories.push(category);
                    this.sortedCategories?.push(category);
                },
                error: (error) => {
                    this.logger.error('Error adding category', error);
                }
            });
        }
    }

    confirmDeleteCategory(categoryId: number): void {
        const confirmed = confirm('Are you sure you want to delete this category?');
        if (confirmed) {
            this.deleteCategory(categoryId);
        }
    }

    deleteCategory(categoryId: number): void {
        this.budgetService.deleteCategory(this.budgetConfiguration!.id, categoryId).subscribe({
            next: () => {
                this.budgetConfiguration = {
                    ...this.budgetConfiguration!,
                    categories: this.budgetConfiguration!.categories.filter(f => f.id !== categoryId)
                };
                this.sortedCategories = this.sortedCategories!.filter(f => f.id !== categoryId);
            },
            error: (error) => {
                this.logger.error('Error deleting category', error);
            }
        });
    }

    onDragStart(category: BudgetCategory, index: number): void {
        this.draggedCategory = category;
        this.dragStartIndex = index;
    }

    onDragOver(event: DragEvent, index: number): void {
        event.preventDefault();
        this.dragTargetIndex = index;
    }

    onDrop(event: DragEvent, index: number): void {
        event.preventDefault();

        if (this.draggedCategory && this.budgetConfiguration) {
            // Save new order
            this.budgetService.reorderCategories(this.budgetConfiguration.id, this.draggedCategory.id!, index + 1).subscribe({
                next: (res) => {
                    this.budgetConfiguration!.categories = res.categories;
                    this.sortedCategories = [...res.categories].sort((a, b) => a.order - b.order);
                },
                error: (err) => {
                    this.logger.error('Failed to reorder categories', err);
                    this.revertDrag();
                }
            });
        }

        this.resetDrag();
    }

    onDragEnd(): void {
        if (this.dragTargetIndex === -1) {
            this.revertDrag();
        }
        this.resetDrag();
    }

    resetDrag(): void {
        this.draggedCategory = null;
        this.dragStartIndex = -1;
        this.dragTargetIndex = -1;
    }

    revertDrag(): void {
        if (this.budgetConfiguration) {
            this.sortedCategories = [...this.budgetConfiguration!.categories];
        }
    }

    preventDecimal(event: KeyboardEvent): void {
        if (event.key === '.' || event.key === ',') {
            event.preventDefault();
        }
    }
}
