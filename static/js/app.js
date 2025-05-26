// JardAIn Garden Planner - Frontend JavaScript

class GardenPlannerApp {
    constructor() {
        this.selectedPlants = new Set();
        this.availablePlants = [];
        this.searchResults = [];
        this.searchTimeout = null;
        this.isSearching = false;
        this.init();
    }

    async init() {
        console.log('🌱 Initializing JardAIn Garden Planner...');
        
        // Load available plants
        await this.loadPlants();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ App initialized successfully!');
    }

    async loadPlants() {
        try {
            console.log('🔍 Loading plants from /api/plants/...');
            const response = await fetch('/api/plants/');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('✅ API Response received:', data);
            console.log('📊 Plants data:', data.plants ? `${data.plants.length} plants` : 'No plants array');
            
            if (data.plants && data.plants.length > 0) {
                console.log('🌱 First plant sample:', data.plants[0]);
            }
            
            this.availablePlants = data.plants || [];
            this.renderPlantGrid();
        } catch (error) {
            console.error('❌ Error loading plants:', error);
            this.showError('Failed to load plant database. Please refresh the page.');
        }
    }

    renderPlantGrid() {
        const plantGrid = document.getElementById('plant-grid');
        if (!plantGrid) {
            console.warn('❌ Plant grid element not found');
            return;
        }

        console.log(`🎨 Rendering ${this.availablePlants.length} plants...`);
        
        if (this.availablePlants.length > 0) {
            console.log('🔍 Sample plant for rendering:', this.availablePlants[0]);
        }

        plantGrid.innerHTML = this.availablePlants.map(plant => {
            const emoji = this.getPlantEmoji(plant.plant_type);
            const plantType = plant.plant_type || 'UNDEFINED';
            
            console.log(`🌱 Rendering ${plant.name}: type="${plantType}", emoji="${emoji}"`);
            
            return `
                <div class="plant-card" data-plant="${plant.name}" onclick="app.togglePlant('${plant.name}')">
                    <div class="plant-emoji">${emoji}</div>
                    <div class="plant-name">${plant.name}</div>
                    <div class="plant-type">${plantType}</div>
                </div>
            `;
        }).join('');
        
        // Ensure visual state matches selection state
        this.syncVisualSelectionState();
        
        console.log(`✅ Rendered ${this.availablePlants.length} plant cards`);
    }
    
    syncVisualSelectionState() {
        // Ensure all plant cards' visual state matches the selectedPlants Set
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            const plantName = card.getAttribute('data-plant');
            const isSelected = this.selectedPlants.has(plantName);
            
            if (isSelected) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
        
        // Update the counter
        this.updateSelectedCount();
    }

    getPlantEmoji(type) {
        const emojis = {
            'fruit': '🍅',
            'vegetable': '🥕',
            'herb': '🌿',
            // Legacy support for more specific types
            'leafy_green': '🥬',
            'root_vegetable': '🥕',
            'legume': '🌱',
            'vine': '🥒',
            'bulb': '🧅',
            'cruciferous': '🥦'
        };
        return emojis[type] || '🌱';
    }

    togglePlant(plantName) {
        const isCurrentlySelected = this.selectedPlants.has(plantName);
        
        if (isCurrentlySelected) {
            this.selectedPlants.delete(plantName);
        } else {
            this.selectedPlants.add(plantName);
        }
        
        // Update visual selection - ensure it matches the actual state
        const plantCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (plantCard) {
            if (isCurrentlySelected) {
                plantCard.classList.remove('selected');
            } else {
                plantCard.classList.add('selected');
            }
        }
        
        // Update selected count
        this.updateSelectedCount();
        
        console.log(`${isCurrentlySelected ? 'Deselected' : 'Selected'} plant: ${plantName}`);
        console.log(`Total selected plants: ${Array.from(this.selectedPlants).join(', ')}`);
    }

    updateSelectedCount() {
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = this.selectedPlants.size;
        }
        
        // Enable/disable generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.disabled = this.selectedPlants.size === 0;
        }
    }

    setupEventListeners() {
        // Generate plan button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateGardenPlan());
        }

        // Enhanced plant search with AI integration
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            // Real-time search with debouncing
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e.target.value));
            
            // Handle autocomplete selection
            searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
            
            // Close autocomplete when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.plant-search')) {
                    this.hideAutocomplete();
                }
            });
        }
    }

    // ========================
    // Enhanced Search Methods
    // ========================
    
    handleSearchInput(searchTerm) {
        // Clear existing timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // If empty search, show all plants and hide autocomplete
        if (!searchTerm.trim()) {
            this.showAllPlants();
            this.hideAutocomplete();
            return;
        }
        
        // Debounce search to avoid excessive API calls
        this.searchTimeout = setTimeout(() => {
            this.performSearch(searchTerm);
        }, 300);
    }
    
    async performSearch(searchTerm) {
        console.log(`🔍 Searching for: "${searchTerm}"`);
        
        this.isSearching = true;
        this.showSearching();
        
        try {
            // First, filter existing static plants for immediate feedback
            this.filterStaticPlants(searchTerm);
            
            // Then, search via API (including potential AI generation)
            const response = await fetch(`/api/plants/search?q=${encodeURIComponent(searchTerm)}&include_generated=false`);
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }
            
            const searchResults = await response.json();
            this.displaySearchResults(searchResults, searchTerm);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError(searchTerm);
        } finally {
            this.isSearching = false;
            this.hideSearching();
        }
    }
    
    filterStaticPlants(searchTerm) {
        const plantCards = document.querySelectorAll('.plant-card');
        const query = searchTerm.toLowerCase();
        
        plantCards.forEach(card => {
            const plantName = card.querySelector('.plant-name').textContent.toLowerCase();
            const plantType = card.querySelector('.plant-type').textContent.toLowerCase();
            
            // Match by name or type
            const matches = plantName.includes(query) || plantType.includes(query);
            card.style.display = matches ? 'block' : 'none';
        });
    }
    
    displaySearchResults(searchResults, originalQuery) {
        const { plants, total_results } = searchResults;
        
        // Show autocomplete dropdown with results
        this.showAutocomplete(plants, originalQuery, total_results);
        
        // If we have results, also filter the main grid
        if (plants.length > 0) {
            this.highlightSearchResults(plants);
        }
    }
    
    showAutocomplete(plants, query, totalResults) {
        // Create or get autocomplete container
        let autocomplete = document.getElementById('search-autocomplete');
        if (!autocomplete) {
            autocomplete = this.createAutocompleteContainer();
        }
        
        // Build autocomplete content
        let content = '';
        
        // Show found plants
        if (plants.length > 0) {
            content += '<div class="autocomplete-section">';
            content += '<div class="autocomplete-header">Found Plants</div>';
            
            plants.forEach(plant => {
                const isStatic = this.availablePlants.some(p => p.name === plant.name);
                const badge = isStatic ? '<span class="plant-badge static">In Garden</span>' : '<span class="plant-badge ai">AI Generated</span>';
                
                content += `
                    <div class="autocomplete-item" onclick="app.selectPlantFromAutocomplete('${plant.name}')">
                        <div class="autocomplete-plant-info">
                            <span class="autocomplete-plant-name">${plant.name}</span>
                            <span class="autocomplete-plant-type">${plant.plant_type}</span>
                        </div>
                        ${badge}
                    </div>
                `;
            });
            content += '</div>';
        }
        
        // Show AI search option if no results
        if (plants.length === 0) {
            content += `
                <div class="autocomplete-section">
                    <div class="autocomplete-header">No plants found in database</div>
                    <div class="autocomplete-ai-option" onclick="app.searchWithAI('${query}')">
                        <div class="ai-search-content">
                            <span class="ai-icon">🤖</span>
                            <div class="ai-search-text">
                                <div class="ai-search-title">Search with AI</div>
                                <div class="ai-search-subtitle">Generate "${query}" information using AI</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        autocomplete.innerHTML = content;
        autocomplete.style.display = 'block';
    }
    
    createAutocompleteContainer() {
        const searchContainer = document.querySelector('.plant-search');
        const autocomplete = document.createElement('div');
        autocomplete.id = 'search-autocomplete';
        autocomplete.className = 'search-autocomplete';
        searchContainer.appendChild(autocomplete);
        return autocomplete;
    }
    
    async searchWithAI(query) {
        console.log(`🤖 Searching with AI for: "${query}"`);
        
        this.hideAutocomplete();
        this.showAISearching(query);
        
        try {
            // Search with AI generation enabled
            const response = await fetch(`/api/plants/search?q=${encodeURIComponent(query)}&include_generated=true`);
            
            if (!response.ok) {
                throw new Error(`AI search failed: ${response.status}`);
            }
            
            const searchResults = await response.json();
            
            console.log('🤖 AI search results:', searchResults);
            console.log('🔍 Plants found:', searchResults.plants?.length || 0);
            
            if (searchResults.plants && searchResults.plants.length > 0) {
                const newPlant = searchResults.plants[0];
                console.log('✅ Adding AI plant to grid:', newPlant);
                this.addAIPlantToGrid(newPlant);
                this.showSuccessMessage(`✅ Found "${newPlant.name}" using AI! Added to your plant options.`);
            } else {
                console.warn('⚠️ No plants in AI search results:', searchResults);
                this.showErrorMessage(`❌ AI couldn't generate information for "${query}". This might not be a valid plant name, or there may be a configuration issue.`);
            }
            
        } catch (error) {
            console.error('AI search error:', error);
            console.error('AI search error details:', {
                message: error.message,
                stack: error.stack,
                query: query
            });
            this.showErrorMessage(`❌ AI search failed: ${error.message}`);
        } finally {
            this.hideAISearching();
        }
    }
    
    addAIPlantToGrid(plant) {
        // Ensure consistent plant name
        const plantName = plant.name.trim();
        
        console.log(`🌱 Adding AI plant "${plantName}" to grid`);
        console.log('🔍 Plant data:', plant);
        
        // Check if plant already exists
        const existingCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (existingCard) {
            console.log(`⚠️ Plant "${plantName}" already exists in grid, selecting it instead`);
            if (!this.selectedPlants.has(plantName)) {
                this.togglePlant(plantName);
            }
            return;
        }
        
        // Add to available plants array  
        this.availablePlants.push(plant);
        
        // Create new plant card with AI badge
        const plantGrid = document.getElementById('plant-grid');
        if (!plantGrid) {
            console.error('❌ Plant grid element not found!');
            return;
        }
        
        const plantCard = document.createElement('div');
        plantCard.className = 'plant-card ai-generated';
        plantCard.setAttribute('data-plant', plantName);
        plantCard.onclick = () => this.togglePlant(plantName);
        
        plantCard.innerHTML = `
            <div class="plant-emoji">${this.getPlantEmoji(plant.plant_type)}</div>
            <div class="plant-name">${plantName}</div>
            <div class="plant-type">${plant.plant_type}</div>
            <div class="plant-badge ai">AI Generated</div>
        `;
        
        // Add to the beginning of the grid
        plantGrid.insertBefore(plantCard, plantGrid.firstChild);
        
        // Auto-select the new plant for user convenience
        this.togglePlant(plantName);
        
        // Highlight the new plant
        setTimeout(() => {
            plantCard.classList.add('newly-added');
            setTimeout(() => plantCard.classList.remove('newly-added'), 2000);
        }, 100);
        
        console.log(`✅ Added AI plant "${plantName}" to grid and selected it`);
    }
    
    selectPlantFromAutocomplete(plantName) {
        // If plant is already in grid, just select it
        const existingCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (existingCard) {
            // Ensure the plant gets selected (not toggled)
            if (!this.selectedPlants.has(plantName)) {
                this.togglePlant(plantName);
            }
            this.hideAutocomplete();
            return;
        }
        
        // If it's an AI plant not in grid, add it
        this.hideAutocomplete();
        this.showInfoMessage(`Adding "${plantName}" to your plant options...`);
        
        // We'll need to fetch the full plant info and add it
        this.fetchAndAddPlant(plantName);
    }
    
    async fetchAndAddPlant(plantName) {
        try {
            const response = await fetch(`/api/plants/${encodeURIComponent(plantName)}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch plant: ${response.status}`);
            }
            
            const plant = await response.json();
            this.addAIPlantToGrid(plant);
            // Note: addAIPlantToGrid already auto-selects the plant, no need to toggle again
            
        } catch (error) {
            console.error('Error fetching plant:', error);
            this.showErrorMessage(`Failed to add "${plantName}": ${error.message}`);
        }
    }
    
    // Utility methods for search UI
    showAllPlants() {
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            card.style.display = 'block';
            // Clear search match highlighting when showing all plants
            card.classList.remove('search-match');
        });
    }
    
    hideAutocomplete() {
        const autocomplete = document.getElementById('search-autocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }
    }
    
    showSearching() {
        // Could add a subtle loading indicator to search box
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            searchInput.classList.add('searching');
        }
    }
    
    hideSearching() {
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            searchInput.classList.remove('searching');
        }
    }
    
    showAISearching(query) {
        this.showInfoMessage(`🤖 AI is analyzing "${query}"... This may take a moment.`);
    }
    
    hideAISearching() {
        // Message will auto-hide
    }
    
    handleSearchKeydown(e) {
        // Handle Enter key, arrow keys for autocomplete navigation
        if (e.key === 'Enter') {
            e.preventDefault();
            // Could select first autocomplete item
        } else if (e.key === 'Escape') {
            this.hideAutocomplete();
        }
    }
    
    highlightSearchResults(plants) {
        // Visual feedback for which plants match search
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            card.classList.remove('search-match');
        });
        
        plants.forEach(plant => {
            const card = document.querySelector(`[data-plant="${plant.name}"]`);
            if (card) {
                card.classList.add('search-match');
            }
        });
    }
    
    showSearchError(query) {
        this.showErrorMessage(`Search failed for "${query}". Please try again.`);
    }
    
    // Message utility methods
    showInfoMessage(message) {
        this.showMessage(message, 'info');
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type = 'info') {
        // Create or get message container
        let messageContainer = document.getElementById('message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'message-container';
            messageContainer.className = 'message-container';
            document.body.appendChild(messageContainer);
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;
        
        // Add to container
        messageContainer.appendChild(messageElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
    }

    async generateGardenPlan() {
        const zipCode = document.getElementById('zip-code').value;
        const gardenSize = document.getElementById('garden-size').value;
        
        if (!zipCode) {
            this.showError('Please enter your zip code.');
            return;
        }
        
        if (this.selectedPlants.size === 0) {
            this.showError('Please select at least one plant.');
            return;
        }

        // Show button loading state
        this.setButtonLoading(true);
        
        // Show loading modal
        this.showLoading();

        try {
            const requestData = {
                zip_code: zipCode,
                selected_plants: Array.from(this.selectedPlants),
                garden_size: gardenSize || 'medium',
                experience_level: 'beginner'
            };

            console.log('🚀 Generating garden plan:', requestData);
            console.log('🔍 Selected plants debug:', Array.from(this.selectedPlants));
            console.log('🔍 Available plants in frontend:', this.availablePlants.map(p => p.name));

            const response = await fetch('/api/plans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const gardenPlan = await response.json();
            console.log('✅ Garden plan generated:', gardenPlan);
            console.log('🔍 Plants in plan:', gardenPlan.plant_information?.map(p => p.name) || 'No plant info');
            
            // Complete the loading animation with celebration
            this.finalizeLoading();
            
            // Wait a moment for the completion animation to be visible
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            this.displayResults(gardenPlan);
            
            // Show PDF download modal
            this.showPDFModal(gardenPlan.plan_id);

        } catch (error) {
            console.error('Error generating garden plan:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                name: error.name,
                timestamp: new Date().toISOString(),
                requestData: requestData
            });
            
            // Provide more detailed error information
            let errorMessage = `Failed to generate garden plan: ${error.message}`;
            
            if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                errorMessage += '\n\n🔧 Troubleshooting tips:\n' +
                              '• Check your internet connection\n' +
                              '• Try refreshing the page\n' +
                              '• Clear your browser cache\n' +
                              '• Try a different browser';
            }
            
            this.showError(errorMessage);
        } finally {
            this.hideLoading();
            this.setButtonLoading(false);
        }
    }

    displayResults(gardenPlan) {
        // Store for debugging
        this.lastGeneratedPlan = gardenPlan;
        
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        // Show only a minimal success message
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>✅ Garden Plan Generated Successfully!</strong><br>
                Your personalized plan for ${gardenPlan.location.city}, ${gardenPlan.location.state} 
                (Zone ${gardenPlan.location.usda_zone}) is ready.<br>
                <small>📱 ${gardenPlan.plant_information.length} plants included • Generated ${new Date().toLocaleDateString()}</small>
            </div>
        `;

        resultsDiv.style.display = 'block';
        
        // Don't scroll to results - let user naturally see the download button
    }

    renderPlantingSchedule(schedules) {
        console.log('🔍 Rendering planting schedules:', schedules);
        
        if (!schedules || !Array.isArray(schedules) || schedules.length === 0) {
            return '<div class="plan-section"><h3>📅 Planting Schedule</h3><p>No planting schedule available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>📅 Planting Schedule</h3>
                <div class="schedule-grid">
                    ${schedules.map(schedule => `
                        <div class="schedule-item">
                            <h4>${schedule.plant_name}</h4>
                            ${schedule.start_indoors_date ? `<p><strong>Start Indoors:</strong> ${schedule.start_indoors_date}</p>` : ''}
                            ${schedule.direct_sow_date ? `<p><strong>Direct Sow:</strong> ${schedule.direct_sow_date}</p>` : ''}
                            ${schedule.transplant_date ? `<p><strong>Transplant:</strong> ${schedule.transplant_date}</p>` : ''}
                            ${schedule.harvest_start_date ? `<p><strong>Harvest Start:</strong> ${schedule.harvest_start_date}</p>` : ''}
                            ${schedule.harvest_end_date ? `<p><strong>Harvest End:</strong> ${schedule.harvest_end_date}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGrowingInstructions(instructions) {
        console.log('🔍 Rendering growing instructions:', instructions);
        
        if (!instructions || !Array.isArray(instructions) || instructions.length === 0) {
            return '<div class="plan-section"><h3>🌱 Growing Instructions</h3><p>No growing instructions available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>🌱 Growing Instructions</h3>
                <div class="instructions-list">
                    ${instructions.map(instruction => `
                        <div class="instruction-item">
                            <h4>${instruction.plant_name}</h4>
                            
                            ${instruction.preparation_steps && instruction.preparation_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🏗️ Preparation Steps</h5>
                                    <ul>
                                        ${instruction.preparation_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.planting_steps && instruction.planting_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌱 Planting Steps</h5>
                                    <ul>
                                        ${instruction.planting_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.care_instructions && instruction.care_instructions.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌿 Care Instructions</h5>
                                    <ul>
                                        ${instruction.care_instructions.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGeneralTips(tips) {
        if (!tips || !Array.isArray(tips) || tips.length === 0) {
            return '';
        }

        return `
            <div class="plan-section">
                <h3>💡 General Tips</h3>
                <ul>
                    ${tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    showPDFModal(planId) {
        // Create modal overlay and modal content
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'pdf-modal-overlay';
        modalOverlay.id = 'pdf-modal-overlay';
        
        modalOverlay.innerHTML = `
            <div class="pdf-modal">
                <button class="pdf-modal-close" id="pdf-modal-close" title="Close">×</button>
                <div class="pdf-modal-content">
                    <div class="pdf-modal-header">
                        <div class="pdf-icon">📄</div>
                        <h2 class="pdf-title">Your Garden Plan is Ready!</h2>
                        <p class="pdf-subtitle">Download your personalized garden plan as a beautiful PDF guide</p>
                    </div>
                    
                    <div class="pdf-features">
                        <div class="feature-item">
                            <div class="feature-icon">📅</div>
                            <div class="feature-text">Personalized planting schedules</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">🌱</div>
                            <div class="feature-text">Detailed growing instructions</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">📐</div>
                            <div class="feature-text">Garden layout recommendations</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">🌍</div>
                            <div class="feature-text">Location-specific advice</div>
                        </div>
                    </div>
                    
                    <div class="pdf-actions">
                        <button class="btn-pdf-download" onclick="app.downloadPDF('${planId}')">
                            📥 Download PDF Garden Plan
                        </button>
                        <button class="btn-pdf-close" onclick="app.closePDFModal()">
                            Maybe Later
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to the body
        document.body.appendChild(modalOverlay);
        
        // Add event listeners for closing the modal
        this.setupPDFModalEventListeners();
        
        // Add entrance animation
        setTimeout(() => {
            modalOverlay.classList.add('show');
        }, 10);
    }

    setupPDFModalEventListeners() {
        const modalOverlay = document.getElementById('pdf-modal-overlay');
        const closeButton = document.getElementById('pdf-modal-close');
        
        // Close modal when clicking the close button
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.closePDFModal();
            });
        }
        
        // Close modal when clicking outside the modal content
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    this.closePDFModal();
                }
            });
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closePDFModal();
            }
        });
    }
    
    closePDFModal() {
        const modalOverlay = document.getElementById('pdf-modal-overlay');
        if (modalOverlay) {
            modalOverlay.classList.remove('show');
            setTimeout(() => {
                if (modalOverlay.parentNode) {
                    modalOverlay.parentNode.removeChild(modalOverlay);
                }
            }, 300);
        }
    }

    async downloadPDF(planId) {
        try {
            // Close the PDF modal first
            this.closePDFModal();
            
            // Show a brief loading message
            this.showSuccess('Generating PDF... Please wait.');
            
            const response = await fetch(`/api/pdf/garden-plan/${planId}`);
            
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `garden-plan-${planId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showSuccess('PDF downloaded successfully!');
        } catch (error) {
            console.error('Error downloading PDF:', error);
            this.showError('Failed to download PDF. Please try again.');
        }
    }

    showLoading() {
        // Create modal overlay and modal content
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'loading-modal-overlay';
        modalOverlay.id = 'loading-modal-overlay';
        
        modalOverlay.innerHTML = `
            <div class="loading-modal">
                <button class="loading-modal-close" id="loading-modal-close" title="Close">×</button>
                <div class="loading-container">
                    <div class="loading-header">
                        <div class="loading-icon">🌱</div>
                        <h2 class="loading-title">Creating Your Garden Plan</h2>
                        <p class="loading-subtitle">Please wait while we generate your personalized garden plan...</p>
                    </div>
                    
                    <div class="loading-animation">
                        <div class="loading-spinner-large">
                            <div class="spinner-leaf">🌱</div>
                        </div>
                        <div class="loading-message" id="loading-message">Analyzing your location and plant selection...</div>
                    </div>
                    
                    <div class="progress-section">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <div class="progress-text" id="progress-text">Processing...</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to the body
        document.body.appendChild(modalOverlay);
        
        // Add event listeners for closing the modal
        this.setupModalEventListeners();
        
        // Start the simple loading animation
        this.startSimpleLoading();
    }

    hideLoading() {
        // Mark animation as completed
        this.animationCompleted = true;
        
        // Clear any running animations
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }
        
        // Remove the modal from the DOM
        const modalOverlay = document.getElementById('loading-modal-overlay');
        if (modalOverlay) {
            // Add fade-out animation before removing
            modalOverlay.style.animation = 'modalFadeOut 0.3s ease-out forwards';
            setTimeout(() => {
                if (modalOverlay.parentNode) {
                    modalOverlay.parentNode.removeChild(modalOverlay);
                }
            }, 300);
        }
        
        console.log('🔄 Loading animation stopped and modal removed');
    }

    // ========================
    // Button State Management
    // ========================
    
    setButtonLoading(isLoading) {
        const generateBtn = document.getElementById('generate-btn');
        const btnText = generateBtn?.querySelector('.btn-text');
        const btnLoading = generateBtn?.querySelector('.btn-loading');
        
        if (!generateBtn || !btnText || !btnLoading) return;
        
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline-flex';
            generateBtn.classList.add('loading');
        } else {
            generateBtn.disabled = false;
            btnText.style.display = 'inline-flex';
            btnLoading.style.display = 'none';
            generateBtn.classList.remove('loading');
        }
    }

    // ========================
    // Modal Event Listeners
    // ========================
    
    setupModalEventListeners() {
        const modalOverlay = document.getElementById('loading-modal-overlay');
        const closeButton = document.getElementById('loading-modal-close');
        
        // Close modal when clicking the close button
        if (closeButton) {
            closeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeLoadingModal();
            });
        }
        
        // Close modal when clicking outside the modal content
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    this.closeLoadingModal();
                }
            });
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', this.handleModalKeydown.bind(this));
    }
    
    handleModalKeydown(e) {
        if (e.key === 'Escape') {
            const modalOverlay = document.getElementById('loading-modal-overlay');
            if (modalOverlay) {
                this.closeLoadingModal();
            }
        }
    }
    
    closeLoadingModal() {
        // Only allow closing if the generation is not in progress
        // You might want to add a confirmation dialog here
        const shouldClose = confirm('Are you sure you want to cancel the garden plan generation?');
        if (shouldClose) {
            this.hideLoading();
            this.setButtonLoading(false);
            // Remove the keydown event listener
            document.removeEventListener('keydown', this.handleModalKeydown.bind(this));
        }
    }
    
    // ========================
    // Simple Loading Animation System
    // ========================
    
    startSimpleLoading() {
        // Initialize simple loading state
        this.loadingProgress = 0;
        this.startTime = Date.now();
        this.animationCompleted = false;
        
        // Calculate estimated time based on number of plants
        const numPlants = this.selectedPlants.size;
        const baseTime = 15000; // 15 seconds base
        const perPlantTime = 1000; // 1 second per plant
        this.estimatedTime = baseTime + (numPlants * perPlantTime);
        
        console.log(`🕐 Loading timing: ${this.estimatedTime/1000}s total for ${numPlants} plants`);
        
        // Start the progress animation
        this.updateSimpleProgress();
        this.animateLoadingMessages();
    }
    
    updateSimpleProgress() {
        this.loadingInterval = setInterval(() => {
            // Don't update if animation is completed
            if (this.animationCompleted) {
                return;
            }
            
            const elapsed = Date.now() - this.startTime;
            
            // Calculate progress percentage (cap at 90% until actual completion)
            this.loadingProgress = Math.min((elapsed / this.estimatedTime) * 100, 90);
            
            // Update progress bar and text
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            
            if (progressFill) {
                progressFill.style.width = `${this.loadingProgress}%`;
            }
            
            if (progressText) {
                const remaining = Math.max(0, Math.ceil((this.estimatedTime - elapsed) / 1000));
                if (remaining > 0) {
                    progressText.textContent = `Processing... ~${remaining}s remaining`;
                } else {
                    progressText.textContent = `Almost done...`;
                }
            }
        }, 200); // Update every 200ms for smooth updates
    }
    
    animateLoadingMessages() {
        const messages = [
            "Analyzing your location and plant selection...",
            "Gathering plant information and requirements...",
            "Creating personalized planting schedules...",
            "Generating detailed growing instructions...",
            "Finalizing your garden plan..."
        ];
        
        let messageIndex = 0;
        const messageElement = document.getElementById('loading-message');
        
        const updateMessage = () => {
            if (this.animationCompleted || !messageElement) {
                return;
            }
            
            messageElement.textContent = messages[messageIndex];
            messageIndex = (messageIndex + 1) % messages.length;
            
            // Schedule next message update
            setTimeout(updateMessage, 3000); // Change message every 3 seconds
        };
        
        updateMessage();
    }
    
    finalizeLoading() {
        console.log('🎉 Finalizing loading animation...');
        
        // Mark animation as completed to stop other processes
        this.animationCompleted = true;
        
        // Complete the progress bar
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const messageElement = document.getElementById('loading-message');
        
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = 'Complete!';
        if (messageElement) messageElement.textContent = 'Your garden plan is ready!';
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    }

    showSuccess(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success';
            successAlert.innerHTML = `<strong>Success:</strong> ${message}`;
            resultsDiv.insertBefore(successAlert, resultsDiv.firstChild);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GardenPlannerApp();
}); 