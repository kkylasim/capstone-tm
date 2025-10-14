import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () => import('./selection-page/selection-page').then(m => m.SelectionPage)
    },
    {
        path: 'end',
        loadComponent: () => import('./end-page/end-page').then(m => m.EndPage)
    }
];
