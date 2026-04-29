<template>
  <div class="min-h-screen bg-slate-100 text-slate-950">
    <section v-if="!session.authenticated" class="flex min-h-screen items-center justify-center p-6">
      <div class="grid w-full max-w-5xl overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:grid-cols-[1.1fr_0.9fr]">
        <div class="bg-slate-950 p-8 text-white">
          <p class="text-sm font-bold uppercase tracking-wide text-emerald-300">FundFlow DAO</p>
          <h1 class="mt-4 text-4xl font-black">Vận hành quỹ minh bạch mà không cần biết blockchain</h1>
          <p class="mt-4 text-slate-300">Luồng chuẩn cho doanh nghiệp nhỏ: thiết lập, ngân sách, hồ sơ, biểu quyết và chi quỹ.</p>
          <div class="mt-8 grid gap-3">
            <div v-for="step in loginFlow" :key="step" class="rounded-lg border border-white/10 bg-white/5 p-3 text-sm">{{ step }}</div>
          </div>
        </div>
        <form class="p-8" @submit.prevent="login">
          <h2 class="text-2xl font-black">Đăng nhập demo</h2>
          <p class="mt-2 text-sm text-slate-600">Dùng tài khoản mẫu để xem phân quyền và workflow SaaS.</p>
          <div class="mt-6 grid gap-4">
            <Field label="Email">
              <select v-model="loginForm.email" class="input-field">
                <option value="admin@fundflow.local">admin@fundflow.local - Quản trị</option>
                <option value="finance@fundflow.local">finance@fundflow.local - Kế toán</option>
                <option value="member@fundflow.local">member@fundflow.local - Thành viên</option>
              </select>
            </Field>
            <Field label="Mật khẩu"><input v-model="loginForm.password" class="input-field" type="password" /></Field>
            <button class="btn-primary">Vào hệ thống</button>
          </div>
          <p class="mt-4 text-xs text-slate-500">Mật khẩu demo: demo123. Nếu backend chưa chạy, app sẽ dùng đăng nhập offline.</p>
        </form>
      </div>
    </section>

    <div v-else class="flex min-h-screen">
      <aside class="hidden w-76 shrink-0 border-r border-slate-200 bg-white lg:block">
        <div class="border-b border-slate-200 p-5">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-700 text-lg font-black text-white">F</div>
            <div>
              <p class="text-lg font-black">FundFlow DAO</p>
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Quản lý quỹ minh bạch</p>
            </div>
          </div>
        </div>

        <div class="p-4">
          <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <p class="text-sm font-bold text-emerald-900">{{ organization.name }}</p>
            <p class="mt-1 text-xs text-emerald-800">Không cần hiểu blockchain để vận hành quỹ.</p>
          </div>

          <nav class="mt-5 space-y-5">
            <div v-for="group in navGroups" :key="group.title">
              <p class="mb-2 px-2 text-xs font-bold uppercase tracking-wide text-slate-400">{{ group.title }}</p>
              <div class="space-y-1">
                <button
                  v-for="item in group.items"
                  :key="item.id"
                  class="flex w-full items-center justify-between rounded-md px-3 py-2.5 text-left text-sm font-semibold transition"
                  :class="activePage === item.id ? 'bg-slate-950 text-white shadow-sm' : 'text-slate-700 hover:bg-slate-100'"
                  @click="activePage = item.id"
                >
                  <span>{{ item.label }}</span>
                  <span v-if="item.count !== undefined" class="rounded bg-white/15 px-2 py-0.5 text-xs">{{ item.count }}</span>
                </button>
              </div>
            </div>
          </nav>
        </div>
      </aside>

      <div class="min-w-0 flex-1">
        <header class="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
          <div class="flex flex-col gap-3 px-4 py-4 lg:flex-row lg:items-center lg:justify-between lg:px-6">
            <div>
              <p class="text-sm font-bold uppercase tracking-wide text-emerald-700">{{ currentPage?.section }}</p>
              <h1 class="mt-1 text-2xl font-black">{{ currentPage?.label }}</h1>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <select v-model="activePage" class="input-field w-full lg:hidden">
                <option v-for="item in navItems" :key="item.id" :value="item.id">{{ item.label }}</option>
              </select>
              <button class="btn-secondary" @click="activePage = nextAction.page">{{ nextAction.label }}</button>
              <button v-if="!account" class="btn-primary" @click="connectWallet">Kết nối ví</button>
              <button v-else class="btn-secondary" @click="loadAll">Đồng bộ</button>
              <span class="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-bold">{{ session.user.name }} · {{ session.user.role }}</span>
              <button class="btn-secondary" @click="logout">Đăng xuất</button>
              <span v-if="account" class="rounded-md border border-slate-200 bg-slate-100 px-3 py-2 text-sm font-bold">{{ shortAddress(account) }}</span>
            </div>
          </div>
        </header>

        <main class="px-4 py-6 lg:px-6">
          <section v-if="activePage === 'command'" class="space-y-6">
            <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div class="grid gap-6 xl:grid-cols-[1fr_360px]">
                <div>
                  <p class="text-sm font-bold uppercase tracking-wide text-emerald-700">Luồng vận hành chuẩn</p>
                  <h2 class="mt-2 text-3xl font-black">Từ thiết lập tổ chức đến chi quỹ có kiểm soát</h2>
                  <p class="mt-3 max-w-3xl text-slate-600">
                    Người dùng chỉ đi theo từng bước nghiệp vụ. Phần ví, token, IPFS và smart contract được giữ ở phía sau như lớp xác thực minh bạch.
                  </p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <p class="text-sm font-bold text-slate-500">Hành động đề xuất</p>
                  <p class="mt-2 text-xl font-black">{{ nextAction.title }}</p>
                  <p class="mt-1 text-sm text-slate-600">{{ nextAction.description }}</p>
                  <button class="btn-primary mt-4 w-full" @click="activePage = nextAction.page">{{ nextAction.label }}</button>
                </div>
              </div>

              <div class="mt-6 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
                <button
                  v-for="step in workflowSteps"
                  :key="step.id"
                  class="rounded-lg border p-4 text-left transition hover:-translate-y-0.5 hover:shadow-sm"
                  :class="step.done ? 'border-emerald-200 bg-emerald-50' : activePage === step.page ? 'border-slate-950 bg-white' : 'border-slate-200 bg-slate-50'"
                  @click="activePage = step.page"
                >
                  <span class="status-pill" :class="step.done ? 'status-ok' : 'status-warn'">{{ step.done ? 'Xong' : 'Cần làm' }}</span>
                  <p class="mt-3 font-black">{{ step.title }}</p>
                  <p class="mt-1 text-sm text-slate-600">{{ step.text }}</p>
                </button>
              </div>
            </section>

            <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard title="Số dư quỹ" :value="`${fmt(stats.treasuryEth)} ETH`" note="Đang giữ trong DAO" />
              <MetricCard title="Đề xuất" :value="String(proposals.length)" note="Dữ liệu blockchain" />
              <MetricCard title="Ngân sách nội bộ" :value="`${fmt(totalBudgetEth)} ETH`" note="Theo kế hoạch vận hành" />
              <MetricCard title="Hồ sơ sẵn sàng" :value="`${selectedFileCount}/3`" note="Tệp cho đề xuất mới" />
            </div>

            <div class="grid gap-6 xl:grid-cols-[1fr_420px]">
              <section class="panel">
                <div class="flex items-center justify-between">
                  <h3 class="section-title">Đề xuất gần đây</h3>
                  <button class="btn-secondary" @click="activePage = 'proposals'">Xem tất cả</button>
                </div>
                <div class="mt-4 space-y-3">
                  <ProposalRow v-for="proposal in proposals.slice(0, 4)" :key="proposal.id" :proposal="proposal" />
                  <EmptyState v-if="proposals.length === 0" title="Chưa có đề xuất" text="Tạo đề xuất đầu tiên sau khi hoàn tất danh bạ và ngân sách." />
                </div>
              </section>
              <section class="panel">
                <h3 class="section-title">Tình trạng quyền hạn</h3>
                <div class="mt-4 space-y-3 text-sm">
                  <InfoRow label="Ví đang dùng" :value="account ? shortAddress(account) : 'Chưa kết nối'" />
                  <InfoRow label="Quyền tạo đề xuất" :value="profile.canPropose ? 'Đã có' : 'Chưa có'" />
                  <InfoRow label="Quyền bỏ phiếu" :value="profile.canVote ? 'Đã có' : 'Chưa có'" />
                  <InfoRow label="Tối thiểu hợp lệ" :value="`${fmt(stats.quorumVotes)} CGT (${stats.quorumPercent || 0}%)`" />
                  <InfoRow label="Thời gian bỏ phiếu" :value="formatDuration(stats.votingPeriodSeconds)" />
                </div>
              </section>
            </div>
          </section>

          <section v-else-if="activePage === 'setup'" class="space-y-6">
            <PageIntro title="Thiết lập tổ chức" text="Tạo hồ sơ tổ chức trước để người dùng thấy đây là sản phẩm nghiệp vụ, không phải màn hình kỹ thuật." />
            <section class="panel">
              <div class="grid gap-3 md:grid-cols-4">
                <button
                  v-for="(step, index) in setupWizard"
                  :key="step.title"
                  class="rounded-lg border p-4 text-left"
                  :class="setupStep === index ? 'border-slate-950 bg-slate-50' : step.done ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white'"
                  @click="setupStep = index"
                >
                  <span class="status-pill" :class="step.done ? 'status-ok' : 'status-warn'">{{ step.done ? 'Xong' : `Bước ${index + 1}` }}</span>
                  <p class="mt-3 font-black">{{ step.title }}</p>
                  <p class="mt-1 text-sm text-slate-600">{{ step.text }}</p>
                </button>
              </div>
            </section>
            <section class="panel">
              <div class="mb-5 flex items-center justify-between gap-3">
                <div>
                  <h3 class="section-title">{{ setupWizard[setupStep].title }}</h3>
                  <p class="mt-1 text-sm text-slate-600">{{ setupWizard[setupStep].text }}</p>
                </div>
                <button class="btn-secondary" @click="setupStep = Math.min(setupWizard.length - 1, setupStep + 1)">Bước tiếp</button>
              </div>
              <form class="grid gap-4 md:grid-cols-2" @submit.prevent="saveOrganization">
                <Field label="Tên tổ chức"><input v-model="organization.name" class="input-field" /></Field>
                <Field label="Người phụ trách"><input v-model="organization.owner" class="input-field" /></Field>
                <Field label="Email liên hệ"><input v-model="organization.email" class="input-field" /></Field>
                <Field label="Loại tổ chức">
                  <select v-model="organization.industry" class="input-field">
                    <option>Câu lạc bộ</option>
                    <option>Doanh nghiệp nhỏ</option>
                    <option>Quỹ cộng đồng</option>
                    <option>Nhóm dự án</option>
                  </select>
                </Field>
                <Field class="md:col-span-2" label="Mô tả"><textarea v-model="organization.description" class="input-field min-h-28" /></Field>
                <button class="btn-primary w-fit">Lưu thiết lập</button>
              </form>
            </section>
          </section>

          <section v-else-if="activePage === 'proposals'" class="space-y-6">
            <PageIntro title="Hồ sơ chi quỹ" text="Luồng này giúp người dùng chuẩn bị đủ thông tin, kiểm tra rủi ro, gửi đề xuất, bỏ phiếu và chi quỹ." />
            <div class="grid gap-3 md:grid-cols-5">
              <FlowCard v-for="step in proposalFlow" :key="step.title" :step="step" />
            </div>

            <div class="grid gap-6 xl:grid-cols-[440px_1fr]">
              <section class="panel h-fit">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <h3 class="section-title">Tạo hồ sơ đề xuất</h3>
                    <p class="mt-1 text-sm text-slate-600">Dùng danh bạ và ngân sách để điền nhanh, sau đó gửi lên DAO.</p>
                  </div>
                  <span class="status-pill" :class="proposalReadiness.ready ? 'status-ok' : 'status-warn'">{{ proposalReadiness.label }}</span>
                </div>

                <div class="mt-4 grid gap-2 md:grid-cols-2">
                  <select class="input-field" @change="applyRecipientById($event.target.value)">
                    <option value="">Chọn người nhận</option>
                    <option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.name }}</option>
                  </select>
                  <select class="input-field" @change="applyBudgetById($event.target.value)">
                    <option value="">Chọn ngân sách</option>
                    <option v-for="budget in budgets" :key="budget.id" :value="budget.id">{{ budget.name }}</option>
                  </select>
                </div>

                <form class="mt-4 grid gap-4" @submit.prevent="createProposal">
                  <Field label="Tên đề xuất"><input v-model="form.title" class="input-field" required /></Field>
                  <Field label="Ví nhận tiền"><input v-model="form.recipient" class="input-field" required /></Field>
                  <Field label="Tóm tắt"><textarea v-model="form.summary" class="input-field min-h-24" required /></Field>
                  <Field label="Số tiền cần chi"><input v-model="form.amountEth" class="input-field" type="number" min="0" step="0.001" required /></Field>
                  <div class="grid gap-3">
                    <FileInput label="Tài liệu đề xuất" accept=".pdf,.md,.txt" @change="form.documentationFile = $event" />
                    <FileInput label="Báo cáo tài chính" accept=".pdf,.csv,.xlsx,.json,.txt" @change="form.financialFile = $event" />
                    <FileInput label="Quy chế biểu quyết" accept=".json" @change="form.rulesFile = $event" />
                  </div>
                  <div class="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">
                    <InfoRow label="Số dư quỹ hiện tại" :value="`${fmt(stats.treasuryEth)} ETH`" />
                    <InfoRow label="Số dư sau chi" :value="`${fmt(treasuryAfterProposal)} ETH`" />
                    <InfoRow label="Tài liệu bắt buộc" :value="`${selectedFileCount}/3`" />
                  </div>
                  <button class="btn-primary" :disabled="busy || !proposalReadiness.ready">{{ busy ? 'Đang gửi...' : 'Gửi đề xuất chi quỹ' }}</button>
                </form>
              </section>

              <section class="panel">
                <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h3 class="section-title">Bảng xử lý đề xuất</h3>
                    <p class="mt-1 text-sm text-slate-600">Theo dõi trạng thái và thao tác tiếp theo cho từng đề xuất.</p>
                  </div>
                  <span class="text-sm font-semibold text-slate-500">{{ proposals.length }} đề xuất</span>
                </div>
                <div class="mt-5 space-y-4">
                  <article v-for="proposal in proposals" :key="proposal.id" class="proposal-card bg-white">
                    <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                      <div>
                        <div class="flex flex-wrap items-center gap-2">
                          <span class="status-pill">#{{ proposal.id }}</span>
                          <span class="status-pill" :class="stateClass(proposal.effectiveState || proposal.state)">{{ proposal.effectiveStateLabel || proposal.stateLabel }}</span>
                          <span v-if="proposal.hasVoted" class="status-pill status-ok">Bạn đã bỏ phiếu</span>
                        </div>
                        <h4 class="mt-3 text-lg font-black">{{ proposal.title }}</h4>
                        <p class="mt-1 text-sm text-slate-600">{{ proposal.summary }}</p>
                      </div>
                      <div class="rounded-lg bg-slate-50 p-3 text-sm lg:w-56">
                        <InfoRow label="Số tiền" :value="`${proposal.amountEth} ETH`" />
                        <InfoRow label="Người nhận" :value="shortAddress(proposal.recipient)" />
                        <p class="mt-2 text-xs text-slate-500">{{ deadlineText(proposal) }}</p>
                      </div>
                    </div>
                    <div class="mt-4 grid gap-3 md:grid-cols-3">
                      <ProgressBar label="Đồng ý" :value="proposal.forVotes" :max="proposal.totalVotes || 1" tone="emerald" />
                      <ProgressBar label="Từ chối" :value="proposal.againstVotes" :max="proposal.totalVotes || 1" tone="rose" />
                      <ProgressBar label="Tối thiểu" :value="proposal.totalVotes" :max="Number(stats.quorumVotes || 1)" tone="sky" />
                    </div>
                    <div class="mt-4 flex flex-wrap gap-2">
                      <button class="btn-secondary" @click="viewCid(proposal.documentationCid, 'Tài liệu đề xuất')">Tài liệu</button>
                      <button class="btn-secondary" @click="viewCid(proposal.financialReportCid, 'Báo cáo tài chính')">Tài chính</button>
                      <button class="btn-secondary" @click="viewCid(proposal.governanceRulesCid, 'Quy chế biểu quyết')">Quy chế</button>
                      <button class="btn-primary" :disabled="busy || !proposal.canVoteNow || proposal.hasVoted || !profile.canVote" @click="castVote(proposal.id, true)">Đồng ý</button>
                      <button class="btn-danger" :disabled="busy || !proposal.canVoteNow || proposal.hasVoted || !profile.canVote" @click="castVote(proposal.id, false)">Từ chối</button>
                      <button class="btn-secondary" :disabled="busy || !proposal.canExecuteNow" @click="executeProposal(proposal.id)">Chi quỹ</button>
                    </div>
                  </article>
                  <EmptyState v-if="proposals.length === 0" title="Chưa có đề xuất" text="Chọn người nhận và ngân sách ở form bên trái để bắt đầu." />
                </div>
              </section>
            </div>
          </section>

          <section v-else-if="activePage === 'recipients'" class="space-y-6">
            <PageIntro title="Danh bạ chi quỹ" text="Quản lý nhà cung cấp, nhân sự và đối tác nhận tiền. User chỉ cần chọn từ danh bạ khi tạo đề xuất." />
            <CrudLayout title="Thêm người nhận" list-title="Danh sách người nhận" :count="recipients.length" :editing="Boolean(recipientForm.id)" @reset="resetRecipientForm">
              <template #form>
                <form class="grid gap-3" @submit.prevent="saveRecipient">
                  <input v-model="recipientForm.name" class="input-field" placeholder="Tên người nhận" required />
                  <input v-model="recipientForm.wallet" class="input-field" placeholder="Địa chỉ ví" required />
                  <div class="grid gap-3 md:grid-cols-2">
                    <select v-model="recipientForm.type" class="input-field"><option>Nhà cung cấp</option><option>Nhân sự</option><option>Đối tác</option><option>Khác</option></select>
                    <select v-model="recipientForm.status" class="input-field"><option>Đang hoạt động</option><option>Tạm dừng</option></select>
                  </div>
                  <input v-model="recipientForm.note" class="input-field" placeholder="Ghi chú" />
                  <button class="btn-primary">{{ recipientForm.id ? 'Cập nhật' : 'Thêm mới' }}</button>
                </form>
              </template>
              <template #list>
                <RecordCard v-for="recipient in recipients" :key="recipient.id" :title="recipient.name" :subtitle="recipient.wallet" :meta="`${recipient.type} · ${recipient.status}`">
                  <button class="btn-secondary" @click="useRecipient(recipient)">Dùng</button>
                  <button class="btn-secondary" @click="editRecipient(recipient)">Sửa</button>
                  <button class="btn-danger" @click="deleteRecipient(recipient.id)">Xóa</button>
                </RecordCard>
              </template>
            </CrudLayout>
          </section>

          <section v-else-if="activePage === 'budgets'" class="space-y-6">
            <PageIntro title="Kế hoạch ngân sách" text="Tạo hạng mục chi trước, sau đó dùng hạng mục này để lập đề xuất có kiểm soát." />
            <CrudLayout title="Thêm hạng mục" list-title="Danh sách ngân sách" :count="budgets.length" :editing="Boolean(budgetForm.id)" @reset="resetBudgetForm">
              <template #form>
                <form class="grid gap-3" @submit.prevent="saveBudget">
                  <input v-model="budgetForm.name" class="input-field" placeholder="Tên hạng mục" required />
                  <input v-model="budgetForm.limitEth" class="input-field" type="number" min="0" step="0.001" placeholder="Hạn mức ETH" required />
                  <input v-model="budgetForm.owner" class="input-field" placeholder="Người phụ trách" />
                  <select v-model="budgetForm.status" class="input-field"><option>Mở</option><option>Tạm dừng</option><option>Đã đóng</option></select>
                  <textarea v-model="budgetForm.description" class="input-field min-h-24" placeholder="Mô tả" />
                  <button class="btn-primary">{{ budgetForm.id ? 'Cập nhật' : 'Thêm mới' }}</button>
                </form>
              </template>
              <template #list>
                <RecordCard v-for="budget in budgets" :key="budget.id" :title="budget.name" :subtitle="`Hạn mức ${fmt(budget.limitEth)} ETH`" :meta="`${budget.owner || 'Chưa phân công'} · ${budget.status}`">
                  <button class="btn-secondary" @click="useBudget(budget)">Dùng</button>
                  <button class="btn-secondary" @click="editBudget(budget)">Sửa</button>
                  <button class="btn-danger" @click="deleteBudget(budget.id)">Xóa</button>
                </RecordCard>
              </template>
            </CrudLayout>
          </section>

          <section v-else-if="activePage === 'members'" class="space-y-6">
            <PageIntro title="Thành viên và vai trò" text="Quản lý người tham gia, vai trò và ví để cấp quyền demo nhanh." />
            <CrudLayout title="Thêm thành viên" list-title="Danh sách thành viên" :count="members.length" :editing="Boolean(memberForm.id)" @reset="resetMemberForm">
              <template #form>
                <form class="grid gap-3" @submit.prevent="saveMember">
                  <input v-model="memberForm.name" class="input-field" placeholder="Họ tên" required />
                  <input v-model="memberForm.email" class="input-field" placeholder="Email" />
                  <input v-model="memberForm.wallet" class="input-field" placeholder="Địa chỉ ví" required />
                  <div class="grid gap-3 md:grid-cols-2">
                    <select v-model="memberForm.role" class="input-field"><option>Quản trị</option><option>Kế toán</option><option>Thành viên</option><option>Người xem</option></select>
                    <select v-model="memberForm.status" class="input-field"><option>Đang hoạt động</option><option>Chờ duyệt</option><option>Tạm khóa</option></select>
                  </div>
                  <button class="btn-primary">{{ memberForm.id ? 'Cập nhật' : 'Thêm thành viên' }}</button>
                </form>
              </template>
              <template #list>
                <RecordCard v-for="member in members" :key="member.id" :title="member.name" :subtitle="member.wallet" :meta="`${member.role} · ${member.status}`">
                  <button class="btn-secondary" @click="fillMintMember(member)">Cấp quyền</button>
                  <button class="btn-secondary" @click="editMember(member)">Sửa</button>
                  <button class="btn-danger" @click="deleteMember(member.id)">Xóa</button>
                </RecordCard>
              </template>
            </CrudLayout>
          </section>

          <section v-else-if="activePage === 'documents'" class="space-y-6">
            <PageIntro title="Kho tài liệu" text="Quản lý hồ sơ pháp lý, tài chính và quy chế trước khi gắn vào đề xuất." />
            <CrudLayout title="Thêm tài liệu" list-title="Kho tài liệu" :count="documents.length" :editing="Boolean(documentForm.id)" @reset="resetDocumentForm">
              <template #form>
                <form class="grid gap-3" @submit.prevent="saveDocument">
                  <input v-model="documentForm.name" class="input-field" placeholder="Tên tài liệu" required />
                  <select v-model="documentForm.type" class="input-field"><option>Đề xuất</option><option>Tài chính</option><option>Quy chế</option><option>Hợp đồng</option></select>
                  <input v-model="documentForm.owner" class="input-field" placeholder="Người phụ trách" />
                  <input v-model="documentForm.cid" class="input-field" placeholder="CID IPFS hoặc link" />
                  <button class="btn-primary">{{ documentForm.id ? 'Cập nhật' : 'Thêm tài liệu' }}</button>
                </form>
              </template>
              <template #list>
                <RecordCard v-for="doc in documents" :key="doc.id" :title="doc.name" :subtitle="doc.cid || 'Chưa có CID'" :meta="`${doc.type} · ${doc.owner || 'Chưa phân công'}`">
                  <button class="btn-secondary" @click="editDocument(doc)">Sửa</button>
                  <button class="btn-danger" @click="deleteDocument(doc.id)">Xóa</button>
                </RecordCard>
              </template>
            </CrudLayout>
          </section>

          <section v-else-if="activePage === 'reports'" class="space-y-6">
            <PageIntro title="Báo cáo điều hành" text="Tổng hợp tình trạng quỹ và dữ liệu vận hành để ban quản lý ra quyết định nhanh." />
            <div class="grid gap-4 md:grid-cols-3">
              <MetricCard title="Đề xuất đã đạt" :value="String(passedProposalCount)" note="Đã thông qua hoặc đã chi" />
              <MetricCard title="Người nhận hoạt động" :value="String(activeRecipientCount)" note="Có thể dùng để chi quỹ" />
              <MetricCard title="Nhật ký thao tác" :value="String(auditLogs.length)" note="Theo dõi hoạt động demo" />
            </div>
            <section class="panel">
              <h3 class="section-title">Tổng hợp dữ liệu</h3>
              <div class="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
                <MiniStat label="Đề xuất" :value="proposals.length" />
                <MiniStat label="Người nhận" :value="recipients.length" />
                <MiniStat label="Ngân sách" :value="budgets.length" />
                <MiniStat label="Thành viên" :value="members.length" />
                <MiniStat label="Tài liệu" :value="documents.length" />
              </div>
            </section>
          </section>

          <section v-else-if="activePage === 'settings'" class="space-y-6">
            <PageIntro title="Cài đặt vận hành" text="Khu vực dành cho quản trị demo: cấp quyền, nạp quỹ và kiểm tra thông số hệ thống." />
            <div class="grid gap-6 xl:grid-cols-2">
              <section class="panel">
                <h3 class="section-title">Cấp quyền demo</h3>
                <div class="mt-4 grid gap-3">
                  <input v-model="mintAddress" class="input-field" placeholder="Địa chỉ ví thành viên" />
                  <div class="grid grid-cols-[1fr_120px] gap-2">
                    <input v-model="mintAmount" class="input-field" placeholder="Số CGT" />
                    <button class="btn-secondary" :disabled="busy" @click="mintTokens">Cấp CGT</button>
                  </div>
                  <button class="btn-secondary" :disabled="busy" @click="mintMembership">Cấp thẻ thành viên</button>
                  <div class="grid grid-cols-[1fr_120px] gap-2">
                    <input v-model="fundAmount" class="input-field" placeholder="ETH nạp quỹ" />
                    <button class="btn-secondary" :disabled="busy" @click="fundTreasury">Nạp quỹ</button>
                  </div>
                </div>
              </section>
              <section class="panel">
                <h3 class="section-title">Thông số hệ thống</h3>
                <div class="mt-4 space-y-3 text-sm">
                  <InfoRow label="DAO" :value="shortAddress(stats.daoAddress)" />
                  <InfoRow label="Token biểu quyết" :value="shortAddress(stats.tokenAddress)" />
                  <InfoRow label="Thẻ thành viên" :value="shortAddress(stats.nftAddress)" />
                  <InfoRow label="Lưu dữ liệu SaaS" value="localStorage / API JSON" />
                </div>
              </section>
            </div>
          </section>

          <section v-else-if="activePage === 'admin'" class="space-y-6">
            <PageIntro title="Quản trị sản phẩm" text="Trang backend cho demo bán hàng: theo dõi audit, xuất dữ liệu và mô tả API." />
            <div class="grid gap-4 md:grid-cols-4">
              <MetricCard title="API" value="/api/saas" note="CRUD backend mẫu" />
              <MetricCard title="Lưu trữ" value="JSON" note="Thay bằng DB khi production" />
              <MetricCard title="Bảo mật" value="Cần bổ sung" note="Đăng nhập và phân quyền" />
              <MetricCard title="Audit" :value="String(auditLogs.length)" note="Nhật ký UI" />
            </div>
            <section class="panel">
              <div class="flex items-center justify-between">
                <h3 class="section-title">Nhật ký thao tác</h3>
                <button class="btn-secondary" @click="exportData">Xuất dữ liệu</button>
              </div>
              <div class="mt-4 space-y-3">
                <RecordCard v-for="log in auditLogs" :key="log.id" :title="log.action" :subtitle="log.time" meta="Audit nội bộ" />
                <EmptyState v-if="auditLogs.length === 0" title="Chưa có nhật ký" text="Các thao tác lưu, xóa, gửi đề xuất sẽ xuất hiện ở đây." />
              </div>
            </section>
          </section>
        </main>
      </div>
    </div>

    <div v-if="detail.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4" @click.self="detail.open = false">
      <div class="max-h-[82vh] w-full max-w-3xl overflow-auto rounded-lg bg-white p-5 shadow-xl">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg font-bold">{{ detail.title }}</h2>
          <button class="btn-secondary" @click="detail.open = false">Đóng</button>
        </div>
        <a class="mt-2 block break-all text-sm font-semibold text-emerald-700" :href="detail.url" target="_blank" rel="noreferrer">{{ detail.cid }}</a>
        <pre v-if="detail.type === 'json' || detail.type === 'text'" class="mt-4 whitespace-pre-wrap rounded-md bg-slate-100 p-4 text-sm">{{ detail.content }}</pre>
        <p v-else class="mt-4 text-slate-700">Tệp này mở tốt nhất qua đường dẫn IPFS phía trên.</p>
      </div>
    </div>

    <div v-if="message" class="fixed bottom-4 left-1/2 z-50 w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 rounded-md bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-lg">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { computed, h, onMounted, reactive, ref } from "vue";
import blockchain from "./utils/blockchain.js";
import { ethers } from "./utils/blockchain.js";
import { retrieveFromIPFS, uploadJsonToIPFS, uploadToIPFS } from "./utils/ipfs.js";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:3002";
const activePage = ref("command");
const account = ref("");
const busy = ref(false);
const message = ref("");
const setupStep = ref(0);
const apiOnline = ref(false);
const session = reactive(loadLocal("ff_session", { authenticated: false, token: "", user: { name: "", email: "", role: "" }, permissions: {} }));
const loginForm = reactive({ email: "admin@fundflow.local", password: "demo123" });
const loginFlow = ["1. Thiết lập tổ chức", "2. Chuẩn hóa danh bạ và ngân sách", "3. Tạo hồ sơ chi quỹ", "4. Biểu quyết và chi quỹ minh bạch"];
const stats = reactive({ treasuryEth: "0", quorumVotes: "0", quorumPercent: 0, votingPeriodSeconds: 0, daoAddress: "", tokenAddress: "", nftAddress: "" });
const profile = reactive({ tokenBalanceFormatted: "0", membershipBalance: 0, totalSupplyFormatted: "0", canPropose: false, canVote: false });
const proposals = ref([]);
const mintAddress = ref("");
const mintAmount = ref("100");
const fundAmount = ref("1");
const form = reactive({ title: "", summary: "", recipient: "", amountEth: "1", documentationFile: null, financialFile: null, rulesFile: null });
const detail = reactive({ open: false, title: "", cid: "", url: "", type: "", content: "" });

const organization = reactive(loadLocal("ff_organization", { name: "Quỹ cộng đồng mẫu", owner: "Ban điều hành", email: "hello@example.com", industry: "Doanh nghiệp nhỏ", description: "Quản lý đề xuất chi quỹ minh bạch cho đội nhóm." }));
const recipients = ref(loadLocal("ff_recipients", [{ id: "r1", name: "Đội vận hành", wallet: "0x90F79bf6EB2c4f870365E785982E1f101E93b906", type: "Nhà cung cấp", note: "Ví nhận tiền demo", status: "Đang hoạt động" }]));
const budgets = ref(loadLocal("ff_budgets", [{ id: "b1", name: "Mua thiết bị văn phòng", limitEth: "1", owner: "Ban tài chính", status: "Mở", description: "Hạng mục mẫu để tạo đề xuất nhanh." }]));
const members = ref(loadLocal("ff_members", [{ id: "m1", name: "Nguyễn Minh", email: "minh@example.com", wallet: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8", role: "Quản trị", status: "Đang hoạt động" }]));
const documents = ref(loadLocal("ff_documents", [{ id: "d1", name: "Quy chế biểu quyết mẫu", type: "Quy chế", owner: "Ban điều hành", cid: "" }]));
const auditLogs = ref(loadLocal("ff_audit", []));

const recipientForm = reactive({ id: "", name: "", wallet: "", type: "Nhà cung cấp", note: "", status: "Đang hoạt động" });
const budgetForm = reactive({ id: "", name: "", limitEth: "", owner: "", status: "Mở", description: "" });
const memberForm = reactive({ id: "", name: "", email: "", wallet: "", role: "Thành viên", status: "Đang hoạt động" });
const documentForm = reactive({ id: "", name: "", type: "Đề xuất", owner: "", cid: "" });

const navGroups = computed(() => [
  { title: "Điều hành", items: [{ id: "command", label: "Trung tâm điều hành" }, { id: "setup", label: "Thiết lập tổ chức" }] },
  { title: "Quy trình chi quỹ", items: [{ id: "proposals", label: "Đề xuất chi quỹ", count: proposals.value.length }, { id: "recipients", label: "Danh bạ nhận tiền", count: recipients.value.length }, { id: "budgets", label: "Ngân sách", count: budgets.value.length }] },
  { title: "Quản trị", items: [{ id: "members", label: "Thành viên", count: members.value.length }, { id: "documents", label: "Tài liệu", count: documents.value.length }, { id: "reports", label: "Báo cáo" }, { id: "settings", label: "Cài đặt" }, { id: "admin", label: "Backend/Admin" }] }
]);
const navItems = computed(() => navGroups.value.flatMap((group) => group.items.map((item) => ({ ...item, section: group.title }))));
const currentPage = computed(() => navItems.value.find((item) => item.id === activePage.value));
const validRecipient = computed(() => ethers.isAddress(form.recipient.trim()));
const selectedFileCount = computed(() => [form.documentationFile, form.financialFile, form.rulesFile].filter(Boolean).length);
const treasuryAfterProposal = computed(() => Math.max(0, Number(stats.treasuryEth || 0) - Number(form.amountEth || 0)));
const activeRecipientCount = computed(() => recipients.value.filter((item) => item.status === "Đang hoạt động").length);
const totalBudgetEth = computed(() => budgets.value.reduce((sum, item) => sum + Number(item.limitEth || 0), 0));
const passedProposalCount = computed(() => proposals.value.filter((item) => [3, 4].includes(item.effectiveState || item.state)).length);
const proposalReadiness = computed(() => {
  if (!account.value) return { ready: false, label: "Cần kết nối ví" };
  if (!profile.canPropose) return { ready: false, label: "Cần thẻ thành viên" };
  if (!validRecipient.value) return { ready: false, label: "Cần địa chỉ nhận hợp lệ" };
  if (Number(form.amountEth || 0) <= 0) return { ready: false, label: "Số ETH chưa hợp lệ" };
  if (Number(form.amountEth || 0) > Number(stats.treasuryEth || 0)) return { ready: false, label: "Vượt số dư quỹ" };
  if (selectedFileCount.value < 3) return { ready: false, label: "Cần đủ tài liệu" };
  return { ready: true, label: "Sẵn sàng gửi" };
});
const workflowSteps = computed(() => [
  { id: 1, title: "Thiết lập", text: "Thông tin tổ chức", page: "setup", done: Boolean(organization.name && organization.owner) },
  { id: 2, title: "Danh bạ", text: "Người nhận tiền", page: "recipients", done: recipients.value.length > 0 },
  { id: 3, title: "Ngân sách", text: "Hạn mức chi", page: "budgets", done: budgets.value.length > 0 },
  { id: 4, title: "Hồ sơ", text: "Đề xuất và tài liệu", page: "proposals", done: proposalReadiness.value.ready || proposals.value.length > 0 },
  { id: 5, title: "Biểu quyết", text: "Thành viên đồng ý", page: "proposals", done: proposals.value.some((item) => item.hasVoted) },
  { id: 6, title: "Chi quỹ", text: "Thực thi tự động", page: "proposals", done: proposals.value.some((item) => (item.effectiveState || item.state) === 4) }
]);
const proposalFlow = computed(() => [
  { title: "1. Chọn người nhận", done: validRecipient.value, text: "Dùng danh bạ đã kiểm tra." },
  { title: "2. Chọn ngân sách", done: Number(form.amountEth || 0) > 0, text: "Có số tiền và mục đích." },
  { title: "3. Đính kèm hồ sơ", done: selectedFileCount.value === 3, text: "Đủ tài liệu bắt buộc." },
  { title: "4. Gửi biểu quyết", done: proposals.value.length > 0, text: "Đề xuất được ghi nhận." },
  { title: "5. Chi quỹ", done: proposals.value.some((item) => (item.effectiveState || item.state) === 4), text: "Khoản chi đã hoàn tất." }
]);
const setupWizard = computed(() => [
  { title: "Hồ sơ tổ chức", text: "Tên, người phụ trách và loại hình.", done: Boolean(organization.name && organization.owner) },
  { title: "Danh bạ nhận tiền", text: "Có ít nhất một người nhận hợp lệ.", done: recipients.value.length > 0 },
  { title: "Kế hoạch ngân sách", text: "Có hạng mục chi để kiểm soát hạn mức.", done: budgets.value.length > 0 },
  { title: "Quyền vận hành", text: "Kết nối ví và cấp quyền demo.", done: Boolean(account.value && profile.canPropose) }
]);
const nextAction = computed(() => {
  const next = workflowSteps.value.find((step) => !step.done) || workflowSteps.value[workflowSteps.value.length - 1];
  return { page: next.page, title: next.title, description: next.text, label: `Tiếp tục: ${next.title}` };
});

function loadLocal(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}
function saveLocal(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}
async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: session.token ? `Bearer ${session.token}` : "",
      ...(options.headers || {})
    }
  });
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).error || "API không phản hồi.");
  if (response.status === 204) return null;
  return response.json();
}
async function loadSaasData() {
  try {
    const [organizations, apiRecipients, apiBudgets, apiMembers, apiDocuments, apiAudit] = await Promise.all([
      apiRequest("/api/saas/organizations"),
      apiRequest("/api/saas/recipients"),
      apiRequest("/api/saas/budgets"),
      apiRequest("/api/saas/members"),
      apiRequest("/api/saas/documents"),
      apiRequest("/api/saas/auditLogs")
    ]);
    apiOnline.value = true;
    if (organizations[0]) Object.assign(organization, organizations[0]);
    recipients.value = apiRecipients;
    budgets.value = apiBudgets;
    members.value = apiMembers;
    documents.value = apiDocuments;
    auditLogs.value = apiAudit.map((item) => ({ id: item.id, action: `${item.action} ${item.resource}`, time: new Date(item.time).toLocaleString("vi-VN") }));
  } catch (error) {
    apiOnline.value = false;
  }
}
async function persistRecord(resource, record, isEditing = false) {
  try {
    const method = isEditing || record.id?.includes("-demo") ? "PUT" : "POST";
    const path = method === "PUT" ? `/api/saas/${resource}/${record.id}` : `/api/saas/${resource}`;
    return await apiRequest(path, { method, body: JSON.stringify(record) });
  } catch {
    return record;
  }
}
async function deleteRemoteRecord(resource, id) {
  try {
    await apiRequest(`/api/saas/${resource}/${id}`, { method: "DELETE" });
  } catch {}
}
async function logAction(action) {
  auditLogs.value = [{ id: Date.now(), action, time: new Date().toLocaleString("vi-VN") }, ...auditLogs.value].slice(0, 30);
  saveLocal("ff_audit", auditLogs.value);
}
const setMessage = (text) => {
  message.value = text;
  window.clearTimeout(setMessage.timer);
  setMessage.timer = window.setTimeout(() => (message.value = ""), 4500);
};
async function login() {
  try {
    const result = await apiRequest("/api/auth/login", { method: "POST", body: JSON.stringify(loginForm) });
    Object.assign(session, { authenticated: true, token: result.token, user: result.user, permissions: result.permissions });
  } catch {
    const role = loginForm.email.startsWith("finance") ? "Kế toán" : loginForm.email.startsWith("member") ? "Thành viên" : "Quản trị";
    Object.assign(session, {
      authenticated: true,
      token: "offline-demo-token",
      user: { name: role, email: loginForm.email, role },
      permissions: { canManageSettings: role === "Quản trị", canManageFinance: ["Quản trị", "Kế toán"].includes(role), canVote: true }
    });
  }
  saveLocal("ff_session", session);
  await loadSaasData();
  setMessage("Đã đăng nhập.");
}
function logout() {
  Object.assign(session, { authenticated: false, token: "", user: { name: "", email: "", role: "" }, permissions: {} });
  saveLocal("ff_session", session);
}

async function saveOrganization() {
  saveLocal("ff_organization", organization);
  await persistRecord("organizations", { ...organization, id: organization.id || "org-demo" }, true);
  logAction("Cập nhật thiết lập tổ chức");
  setMessage("Đã lưu thiết lập tổ chức.");
}
async function saveRecipient() {
  const wallet = recipientForm.wallet.trim();
  if (!ethers.isAddress(wallet)) return setMessage("Địa chỉ ví người nhận không hợp lệ.");
  const isEditing = Boolean(recipientForm.id);
  const record = { ...recipientForm, id: recipientForm.id || `r${Date.now()}`, name: recipientForm.name.trim(), wallet, note: recipientForm.note.trim() };
  recipients.value = recipientForm.id ? recipients.value.map((item) => (item.id === record.id ? record : item)) : [record, ...recipients.value];
  saveLocal("ff_recipients", recipients.value);
  await persistRecord("recipients", record, isEditing);
  resetRecipientForm();
  logAction("Lưu người nhận");
}
function editRecipient(item) { Object.assign(recipientForm, item); }
async function deleteRecipient(id) { if (window.confirm("Xóa người nhận này?")) { recipients.value = recipients.value.filter((item) => item.id !== id); saveLocal("ff_recipients", recipients.value); await deleteRemoteRecord("recipients", id); logAction("Xóa người nhận"); } }
function resetRecipientForm() { Object.assign(recipientForm, { id: "", name: "", wallet: "", type: "Nhà cung cấp", note: "", status: "Đang hoạt động" }); }
function useRecipient(item) { form.recipient = item.wallet; if (!form.title) form.title = `Chi trả cho ${item.name}`; if (!form.summary) form.summary = item.note || `Đề xuất chi quỹ cho ${item.name}.`; activePage.value = "proposals"; }
function applyRecipientById(id) { const item = recipients.value.find((record) => record.id === id); if (item) useRecipient(item); }

async function saveBudget() {
  const limitEth = Number(budgetForm.limitEth || 0);
  if (limitEth <= 0) return setMessage("Hạn mức ngân sách phải lớn hơn 0.");
  const isEditing = Boolean(budgetForm.id);
  const record = { ...budgetForm, id: budgetForm.id || `b${Date.now()}`, name: budgetForm.name.trim(), limitEth: String(limitEth) };
  budgets.value = budgetForm.id ? budgets.value.map((item) => (item.id === record.id ? record : item)) : [record, ...budgets.value];
  saveLocal("ff_budgets", budgets.value);
  await persistRecord("budgets", record, isEditing);
  resetBudgetForm();
  logAction("Lưu ngân sách");
}
function editBudget(item) { Object.assign(budgetForm, item); }
async function deleteBudget(id) { if (window.confirm("Xóa ngân sách này?")) { budgets.value = budgets.value.filter((item) => item.id !== id); saveLocal("ff_budgets", budgets.value); await deleteRemoteRecord("budgets", id); logAction("Xóa ngân sách"); } }
function resetBudgetForm() { Object.assign(budgetForm, { id: "", name: "", limitEth: "", owner: "", status: "Mở", description: "" }); }
function useBudget(item) { form.title = item.name; form.amountEth = item.limitEth; form.summary = item.description || `Đề xuất chi quỹ cho ${item.name}.`; activePage.value = "proposals"; }
function applyBudgetById(id) { const item = budgets.value.find((record) => record.id === id); if (item) useBudget(item); }

async function saveMember() {
  if (!ethers.isAddress(memberForm.wallet.trim())) return setMessage("Địa chỉ ví thành viên không hợp lệ.");
  const isEditing = Boolean(memberForm.id);
  const record = { ...memberForm, id: memberForm.id || `m${Date.now()}` };
  members.value = memberForm.id ? members.value.map((item) => (item.id === record.id ? record : item)) : [record, ...members.value];
  saveLocal("ff_members", members.value);
  await persistRecord("members", record, isEditing);
  resetMemberForm();
  logAction("Lưu thành viên");
}
function editMember(item) { Object.assign(memberForm, item); }
async function deleteMember(id) { if (window.confirm("Xóa thành viên này?")) { members.value = members.value.filter((item) => item.id !== id); saveLocal("ff_members", members.value); await deleteRemoteRecord("members", id); logAction("Xóa thành viên"); } }
function resetMemberForm() { Object.assign(memberForm, { id: "", name: "", email: "", wallet: "", role: "Thành viên", status: "Đang hoạt động" }); }
function fillMintMember(item) { mintAddress.value = item.wallet; activePage.value = "settings"; setMessage("Đã điền ví thành viên vào trang cài đặt."); }

async function saveDocument() {
  const isEditing = Boolean(documentForm.id);
  const record = { ...documentForm, id: documentForm.id || `d${Date.now()}` };
  documents.value = documentForm.id ? documents.value.map((item) => (item.id === record.id ? record : item)) : [record, ...documents.value];
  saveLocal("ff_documents", documents.value);
  await persistRecord("documents", record, isEditing);
  resetDocumentForm();
  logAction("Lưu tài liệu");
}
function editDocument(item) { Object.assign(documentForm, item); }
async function deleteDocument(id) { if (window.confirm("Xóa tài liệu này?")) { documents.value = documents.value.filter((item) => item.id !== id); saveLocal("ff_documents", documents.value); await deleteRemoteRecord("documents", id); logAction("Xóa tài liệu"); } }
function resetDocumentForm() { Object.assign(documentForm, { id: "", name: "", type: "Đề xuất", owner: "", cid: "" }); }
function exportData() { navigator.clipboard?.writeText(JSON.stringify({ organization, recipients: recipients.value, budgets: budgets.value, members: members.value, documents: documents.value }, null, 2)); setMessage("Đã sao chép dữ liệu demo vào clipboard."); }

async function connectWallet() {
  try {
    const ok = await blockchain.connect();
    if (!ok) return setMessage("Không tìm thấy MetaMask hoặc ví EVM tương thích.");
    account.value = await blockchain.getAccount();
    mintAddress.value = account.value;
    await loadAll();
    const walletProvider = blockchain.getWalletProvider();
    walletProvider?.on?.("accountsChanged", () => window.location.reload());
    walletProvider?.on?.("chainChanged", () => window.location.reload());
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  }
}
async function loadAll() {
  if (!blockchain.provider && !blockchain.signer) return;
  try {
    Object.assign(stats, await blockchain.getDaoStats());
    if (account.value) Object.assign(profile, await blockchain.getMemberProfile(account.value));
    proposals.value = (await blockchain.getProposals(account.value)).map(applyLocalDeadlineState);
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  }
}
function applyLocalDeadlineState(proposal) {
  const now = Math.floor(Date.now() / 1000);
  const quorumReached = proposal.totalVotes >= Number(stats.quorumVotes || 0);
  const majorityFor = proposal.forVotes > proposal.againstVotes;
  const deadlinePassed = now > proposal.endTime;
  const decorated = { ...proposal, canVoteNow: proposal.state === 1 && !deadlinePassed };
  if (proposal.executed || proposal.state === 4) return { ...decorated, effectiveState: 4, effectiveStateLabel: "Đã thực thi", canExecuteNow: false };
  if (deadlinePassed && quorumReached && majorityFor) return { ...decorated, effectiveState: 3, effectiveStateLabel: "Đã thông qua", canExecuteNow: true };
  if (deadlinePassed) return { ...decorated, effectiveState: 2, effectiveStateLabel: "Không đạt", canExecuteNow: false };
  return { ...decorated, effectiveState: proposal.state, effectiveStateLabel: proposal.stateLabel, canExecuteNow: proposal.canExecute };
}
async function createProposal() {
  const recipient = form.recipient.trim();
  if (!proposalReadiness.value.ready) return setMessage(proposalReadiness.value.label);
  if (!window.confirm(`Tạo đề xuất chi ${form.amountEth} ETH cho ví ${shortAddress(recipient)}?`)) return;
  busy.value = true;
  try {
    setMessage("Đang tải tài liệu lên IPFS...");
    const documentationCid = await uploadToIPFS(form.documentationFile);
    const financialReportCid = await uploadToIPFS(form.financialFile);
    const governanceRulesCid = form.rulesFile.type === "application/json" ? await uploadToIPFS(form.rulesFile) : await uploadJsonToIPFS({ title: form.title, summary: form.summary });
    setMessage("Vui lòng xác nhận giao dịch trong ví.");
    await blockchain.propose({ ...form, recipient, title: form.title.trim(), summary: form.summary.trim(), documentationCid, financialReportCid, governanceRulesCid });
    Object.assign(form, { title: "", summary: "", recipient: "", amountEth: "1", documentationFile: null, financialFile: null, rulesFile: null });
    logAction("Tạo đề xuất on-chain");
    setMessage("Đã tạo đề xuất thành công.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}
async function castVote(proposalId, support) {
  if (!window.confirm(`Xác nhận ${support ? "đồng ý" : "từ chối"} đề xuất #${proposalId}?`)) return;
  busy.value = true;
  try {
    await blockchain.vote(proposalId, support);
    logAction("Bỏ phiếu on-chain");
    setMessage("Đã ghi nhận phiếu.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}
async function executeProposal(proposalId) {
  const proposal = proposals.value.find((item) => item.id === proposalId);
  if (!window.confirm(`Chi ${proposal?.amountEth || ""} ETH từ quỹ?`)) return;
  busy.value = true;
  try {
    await blockchain.execute(proposalId);
    logAction("Thực thi chi quỹ on-chain");
    setMessage("Đã thực thi đề xuất.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}
async function mintTokens() {
  if (!ethers.isAddress(mintAddress.value.trim())) return setMessage("Địa chỉ ví không hợp lệ.");
  busy.value = true;
  try { await blockchain.mintTokens(mintAddress.value.trim(), mintAmount.value); setMessage("Đã cấp CGT."); await loadAll(); }
  catch (error) { setMessage(error.shortMessage || error.message); }
  finally { busy.value = false; }
}
async function mintMembership() {
  if (!ethers.isAddress(mintAddress.value.trim())) return setMessage("Địa chỉ ví không hợp lệ.");
  busy.value = true;
  try { await blockchain.mintMembership(mintAddress.value.trim()); setMessage("Đã cấp thẻ thành viên."); await loadAll(); }
  catch (error) { setMessage(error.shortMessage || error.message); }
  finally { busy.value = false; }
}
async function fundTreasury() {
  if (!fundAmount.value) return;
  busy.value = true;
  try { await blockchain.fundTreasury(fundAmount.value); setMessage("Đã nạp quỹ."); await loadAll(); }
  catch (error) { setMessage(error.shortMessage || error.message); }
  finally { busy.value = false; }
}
async function viewCid(cid, title) {
  detail.open = true; detail.title = title; detail.cid = cid; detail.url = ""; detail.type = ""; detail.content = "Đang tải từ IPFS...";
  try { const result = await retrieveFromIPFS(cid); detail.url = result.url; detail.type = result.type; detail.content = result.type === "json" ? JSON.stringify(result.content, null, 2) : result.content || ""; }
  catch (error) { detail.content = error.message; }
}
function shortAddress(address) { return address ? `${address.slice(0, 6)}...${address.slice(-4)}` : "-"; }
function fmt(value) { return Number(value || 0).toLocaleString("vi-VN", { maximumFractionDigits: 4 }); }
function formatDuration(seconds) { if (!seconds) return "-"; return seconds < 3600 ? `${Math.round(seconds / 60)} phút` : `${Math.round(seconds / 3600)} giờ`; }
function formatDate(timestamp) { return new Date(timestamp * 1000).toLocaleString("vi-VN"); }
function deadlineText(proposal) { const now = Math.floor(Date.now() / 1000); if (proposal.effectiveState === 4) return "Đã hoàn tất"; if (now > proposal.endTime) return `Đã hết hạn lúc ${formatDate(proposal.endTime)}`; return `Còn ${formatDuration(proposal.endTime - now)}, hết hạn ${formatDate(proposal.endTime)}`; }
function stateClass(state) { return { 1: "status-live", 2: "status-warn", 3: "status-ok", 4: "status-done" }[state]; }

const InfoRow = (props) => h("div", { class: "flex items-center justify-between gap-3 border-b border-slate-100 pb-2 last:border-b-0" }, [h("span", { class: "text-slate-500" }, props.label), h("span", { class: "break-all text-right font-semibold" }, props.value || "-")]);
InfoRow.props = ["label", "value"];
const PageIntro = (props) => h("section", { class: "rounded-lg border border-slate-200 bg-white p-5 shadow-sm" }, [h("p", { class: "text-sm font-bold uppercase tracking-wide text-emerald-700" }, "Quy trình"), h("h2", { class: "mt-2 text-2xl font-black" }, props.title), h("p", { class: "mt-2 max-w-3xl text-sm text-slate-600" }, props.text)]);
PageIntro.props = ["title", "text"];
const Field = (props, { slots }) => h("label", { class: props.class || "block" }, [h("span", { class: "mb-2 block text-sm font-bold text-slate-700" }, props.label), slots.default?.()]);
Field.props = ["label", "class"];
const MetricCard = (props) => h("section", { class: "panel" }, [h("p", { class: "text-sm text-slate-500" }, props.title), h("p", { class: "mt-2 text-3xl font-black" }, props.value), h("p", { class: "mt-1 text-sm text-slate-500" }, props.note)]);
MetricCard.props = ["title", "value", "note"];
const MiniStat = (props) => h("div", { class: "rounded-lg border border-slate-200 bg-slate-50 p-4" }, [h("p", { class: "text-sm text-slate-500" }, props.label), h("p", { class: "mt-1 text-2xl font-black" }, String(props.value))]);
MiniStat.props = ["label", "value"];
const FlowCard = (props) => h("div", { class: `rounded-lg border p-4 ${props.step.done ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-white"}` }, [h("span", { class: `status-pill ${props.step.done ? "status-ok" : "status-warn"}` }, props.step.done ? "Xong" : "Đợi"), h("p", { class: "mt-3 font-black" }, props.step.title), h("p", { class: "mt-1 text-sm text-slate-600" }, props.step.text)]);
FlowCard.props = ["step"];
const EmptyState = (props) => h("div", { class: "rounded-lg border border-dashed border-slate-300 bg-slate-50 p-8 text-center" }, [h("p", { class: "font-black text-slate-700" }, props.title), h("p", { class: "mt-1 text-sm text-slate-500" }, props.text)]);
EmptyState.props = ["title", "text"];
const ProposalRow = (props) => h("div", { class: "rounded-lg border border-slate-200 bg-slate-50 p-4" }, [h("div", { class: "flex items-center justify-between gap-3" }, [h("div", [h("p", { class: "font-black" }, props.proposal.title), h("p", { class: "mt-1 text-sm text-slate-500" }, `${props.proposal.amountEth} ETH · ${shortAddress(props.proposal.recipient)}`)]), h("span", { class: `status-pill ${stateClass(props.proposal.effectiveState || props.proposal.state)}` }, props.proposal.effectiveStateLabel || props.proposal.stateLabel)])]);
ProposalRow.props = ["proposal"];
const CrudLayout = (props, { slots, emit }) => h("div", { class: "grid gap-6 xl:grid-cols-[420px_1fr]" }, [h("section", { class: "panel h-fit" }, [h("div", { class: "mb-4 flex items-center justify-between" }, [h("h3", { class: "section-title" }, props.title), props.editing ? h("button", { class: "btn-secondary", onClick: () => emit("reset") }, "Tạo mới") : null]), slots.form?.()]), h("section", { class: "panel" }, [h("div", { class: "mb-4 flex items-center justify-between" }, [h("h3", { class: "section-title" }, props.listTitle), h("span", { class: "text-sm text-slate-500" }, `${props.count} bản ghi`)]), h("div", { class: "space-y-3" }, slots.list?.())])]);
CrudLayout.props = ["title", "listTitle", "count", "editing"];
CrudLayout.emits = ["reset"];
const RecordCard = (props, { slots }) => h("article", { class: "table-card" }, [h("div", { class: "min-w-0" }, [h("p", { class: "font-black" }, props.title), h("p", { class: "mt-1 break-all text-sm text-slate-600" }, props.subtitle), h("p", { class: "mt-1 text-sm text-slate-500" }, props.meta)]), h("div", { class: "flex flex-wrap gap-2" }, slots.default?.())]);
RecordCard.props = ["title", "subtitle", "meta"];
const FileInput = (props, { emit }) => h("label", { class: "block" }, [h("span", { class: "mb-2 block text-sm font-bold text-slate-700" }, props.label), h("input", { class: "input-field file:mr-3 file:rounded-md file:border-0 file:bg-slate-200 file:px-3 file:py-2 file:text-sm file:font-semibold", type: "file", accept: props.accept, onChange: (event) => emit("change", event.target.files?.[0] || null) })]);
FileInput.props = ["label", "accept"];
FileInput.emits = ["change"];
const ProgressBar = (props) => { const percent = computed(() => Math.min(100, Math.round((Number(props.value || 0) / Number(props.max || 1)) * 100))); return h("div", { class: "rounded-lg border border-slate-200 bg-white p-3" }, [h("div", { class: "mb-2 flex justify-between text-sm" }, [h("span", { class: "font-semibold" }, props.label), h("span", { class: "text-slate-500" }, fmt(props.value))]), h("div", { class: "h-2 overflow-hidden rounded bg-slate-100" }, [h("div", { class: `h-full progress-${props.tone}`, style: { width: `${percent.value}%` } })])]); };
ProgressBar.props = ["label", "value", "max", "tone"];
onMounted(() => {
  if (session.authenticated) loadSaasData();
});
if (blockchain.isDevAutoWalletEnabled()) connectWallet();
</script>
