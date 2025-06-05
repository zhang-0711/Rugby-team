// 比赛管理模态框脚本
document.addEventListener('DOMContentLoaded', function() {
    // 初始化模态框
    var matchDetailsModal = document.getElementById('matchDetailsModal');
    if (matchDetailsModal) {
        matchDetailsModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var matchId = button.getAttribute('data-match-id');
            
            // 实际应用中，会根据ID加载比赛数据
            // 这里模拟不同类型的比赛
            
            var modalStatus = document.getElementById('modalStatus');
            var completedSection = document.getElementById('completedMatchSection');
            var upcomingSection = document.getElementById('upcomingMatchSection');
            
            if (matchId === '2') {
                // 即将到来的比赛
                modalStatus.textContent = 'Upcoming';
                modalStatus.className = 'badge bg-primary';
                document.getElementById('modalMatchDate').textContent = '21 Apr 2025';
                document.getElementById('modalMatchTime').textContent = '15:00';
                document.getElementById('modalVenue').textContent = 'Lions Stadium';
                document.getElementById('modalSquad').textContent = 'Senior Team';
                document.getElementById('modalNotes').textContent = 'Key match for the season';
                document.getElementById('modalHomeTeam').textContent = 'Edinburgh Lions';
                document.getElementById('modalAwayTeam').textContent = 'Simply Rugby';
                
                completedSection.style.display = 'none';
                upcomingSection.style.display = 'block';
            } else {
                // 已完成的比赛
                var isWin = matchId === '1';
                modalStatus.textContent = isWin ? 'Win' : 'Loss';
                modalStatus.className = isWin ? 'badge bg-success' : 'badge bg-danger';
                
                document.getElementById('modalMatchDate').textContent = isWin ? '12 Apr 2025' : '5 Apr 2025';
                document.getElementById('modalMatchTime').textContent = isWin ? '14:30' : '13:00';
                document.getElementById('modalVenue').textContent = isWin ? 'Home Ground' : 'Aberdeen Stadium';
                document.getElementById('modalSquad').textContent = isWin ? 'Senior Team' : 'Junior Team U16';
                document.getElementById('modalNotes').textContent = isWin ? 'Great team effort' : 'Need to improve defensive strategy';
                
                if (isWin) {
                    document.getElementById('modalHomeTeam').textContent = 'Simply Rugby';
                    document.getElementById('modalAwayTeam').textContent = 'Glasgow Eagles';
                    document.getElementById('modalHomeScore').value = '24';
                    document.getElementById('modalAwayScore').value = '18';
                } else {
                    document.getElementById('modalHomeTeam').textContent = 'Aberdeen United';
                    document.getElementById('modalAwayTeam').textContent = 'Simply Rugby';
                    document.getElementById('modalHomeScore').value = '28';
                    document.getElementById('modalAwayScore').value = '15';
                }
                
                completedSection.style.display = 'block';
                upcomingSection.style.display = 'none';
            }
        });
    }
    
    // 设置新比赛模态框的当前日期
    var matchDateInput = document.getElementById('matchDate');
    if (matchDateInput) {
        var today = new Date();
        var dateString = today.toISOString().split('T')[0];
        matchDateInput.value = dateString;
    }
    
    // 筛选按钮
    var filterBtn = document.querySelector('.btn-outline-primary');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            // 实际应用中，会根据筛选条件过滤比赛
            alert('Filters applied successfully!');
        });
    }
    
    // 保存新比赛按钮
    var saveNewMatchBtn = document.getElementById('saveNewMatch');
    if (saveNewMatchBtn) {
        saveNewMatchBtn.addEventListener('click', function() {
            // 实际应用中，会保存新比赛
            alert('New match created successfully!');
            var modal = bootstrap.Modal.getInstance(document.getElementById('newMatchModal'));
            modal.hide();
        });
    }
    
    // 保存比赛详情按钮
    var saveMatchDetailsBtn = document.getElementById('saveMatchDetails');
    if (saveMatchDetailsBtn) {
        saveMatchDetailsBtn.addEventListener('click', function() {
            // 实际应用中，会保存比赛详情
            alert('Match details updated successfully!');
            var modal = bootstrap.Modal.getInstance(document.getElementById('matchDetailsModal'));
            modal.hide();
        });
    }
    
    // 删除比赛按钮
    var deleteMatchBtn = document.getElementById('deleteMatch');
    if (deleteMatchBtn) {
        deleteMatchBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this match?')) {
                // 实际应用中，会删除比赛
                alert('Match deleted successfully!');
                var modal = bootstrap.Modal.getInstance(document.getElementById('matchDetailsModal'));
                modal.hide();
            }
        });
    }
});
