import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BudgetSettingsTabComponent } from './budget-settings-tab.component';

describe('BudgetSettingsTabComponent', () => {
  let component: BudgetSettingsTabComponent;
  let fixture: ComponentFixture<BudgetSettingsTabComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BudgetSettingsTabComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BudgetSettingsTabComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
